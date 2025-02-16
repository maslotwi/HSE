import struct
import subprocess
import consts
import collections
import time
from dataclasses import dataclass
from os.path import join
from re import search, MULTILINE, finditer, DOTALL
from typing import List, Tuple
from array import array
from threading import Lock, Thread

class ProcessNotFound(Exception):
    pass


class FakeThread:
    def __init__(self):
        pass
    def join(self):
        return True
    def is_alive(self):
        return True

@dataclass(frozen=True, order=True)
class Skill:
    id: int
    lvl: int
    slot: int

    @property
    def name(self):
        return consts.skill_names[self.id]


@dataclass()
class Player:
    color: int
    heroes: List[str]
    name: str
    resources: List[int]
    selected_town: int | None
    towns: List[int]


@dataclass(frozen=True, order=True)
class Troop:
    id: int
    amount: int

    @property
    def name(self):
        return consts.troop_names.get(self.id, '')


Town = collections.namedtuple('Town', ["id", "owner", "built_this_turn", "type", "x", "y", "underground"])


class H3editor:
    @dataclass(frozen=True, order=True)
    class HeroLocation:
        main: int
        slots: int

    def __init__(self, process_name="h3hota HD.exe"):
        self.hero_loader: Thread | None = None
        self.hero_loader_progress: float = 0.
        self.hero_location_neighbourhood: int | None = None
        self.slots_location_neighbourhood: int | None = None
        self.process_name: str = process_name
        self.rw_lock: Lock = Lock()
        self.PID = None
        self.memory_file = None
        self.mem_locations = None
        self.reload()

    def reload(self):
        self.get_PID()
        if self.PID is not None:
            self.open_memory_file()
            with open("cache") as f:
                data = f.read().splitlines()
                self.hero_location_neighbourhood = int(data[0], base=16)
                self.slots_location_neighbourhood = int(data[1], base=16)
            if self.hero_loader is not None and self.hero_loader.is_alive():
                self.hero_loader.join()
            self.hero_loader = Thread(target=self.get_hero_locations)
            self.hero_loader.start()
            self.get_managers()
            self.get_game_map()
            self.get_player_locations()
            self.get_town_locations()
            self.get_map_size()

    def __del__(self):
        if self.memory_file is not None:
            self.memory_file.close()

    def open_memory_file(self):
        self.get_PID()
        if self.PID is None:
            raise ProcessNotFound("Could not find Heroes 3 process")

        proc = join("/proc", str(self.PID))
        self.memory_file = open(join(proc, "mem"), "rb+")

    def get_PID(self):
        try:
            pid = subprocess.check_output(["pgrep", "-o", self.process_name])
            self.PID = int(pid)
        except subprocess.CalledProcessError:
            self.PID = None

    def get_managers(self):
        self.game_mgr = self.dereference(consts.game_manager_address)
        self.adv_mgr = self.dereference(consts.adventure_manager_address)

    def get_game_map(self):
        self.game_map = self.dereference(self.adv_mgr + consts.game_map)

    def get_player_locations(self):
        self.players_array = self.game_mgr + consts.player_array - consts.player_color

    def get_town_locations(self):
        self.town_array = self.dereference(self.game_mgr + consts.town_array)

    def get_map_size(self):
        self.map_size = self.dereference(self.game_map + consts.map_size)

    def get_player(self, color: int):
        with self.rw_lock:
            self.memory_file.seek(self.players_array + consts.player_heroes + color * 360)
            hero_array = array('I')
            hero_array.frombytes(self.memory_file.read(4 * 8))
            hero_array = [consts.hero_ids[i] for i in hero_array if i < 256]

            self.memory_file.seek(self.players_array + consts.player_resources + color * 360)
            resource_array = array('i')
            resource_array.frombytes(self.memory_file.read(4 * 7))

            self.memory_file.seek(self.players_array + color * 360)
            name = self.memory_file.read(21)
            try:
                name = name[:name.index(b"\x00")].decode("ascii")
            except (UnicodeDecodeError, ValueError):
                print(name)

            self.memory_file.seek(self.players_array + color * 360 + consts.player_selected_town - 1)
            town_count, selected = self.memory_file.read(2)
            if selected == 255:
                selected = None

            return Player(color, hero_array, name, resource_array.tolist(), selected, list(self.memory_file.read(town_count)))

    def set_resources(self, color: int, resources: List[int]):
        with self.rw_lock:
            self.memory_file.seek(self.players_array + consts.player_resources + color * 360)
            resource_array = array('i', resources)
            self.memory_file.write(resource_array.tobytes())

    @staticmethod
    def __resolve_duplicates(hero_locs: List[Tuple[str, int]]) -> List[int]:
        names = {i[0]:list() for i in hero_locs}
        for i, (name, loc) in enumerate(hero_locs):
            names[name].append(i)

        duplicates = [name for name in names if len(names[name]) != 1]

        delete_list = []

        for name in duplicates:
            keep_id = 0
            mean_distance = float("inf")
            for index in names[name]:
                dist_sum = 0
                for _, loc in hero_locs:
                    dist_sum += abs(loc - hero_locs[index][1])
                if dist_sum < mean_distance:
                    mean_distance = dist_sum
                    keep_id = index
            for index in names[name]:
                if index != keep_id:
                    delete_list.append(index)

        return delete_list

    def __cmp_n_back(self, position, n, sl, hr) -> bool:
        for i in range(n):
            n_slot = self.dereference(sl[position-i-1], "B"*consts.total_secondary_skill_count)
            n_hero = self.dereference(hr[position-i-1][1]+consts.secondary_skills, "B"*consts.total_secondary_skill_count)
            for j in range(consts.total_secondary_skill_count):
                if (n_hero[j] == 0 and n_slot[j] != 0) or (n_hero[j] != 0 and n_slot[j] == 0):
                    return False
        return True


    def __rotate_slots(self, original_slots: List[int], hero_mem: List[Tuple[str,int]]) -> List[int]:
        result = original_slots.copy()

        first_okay = len(original_slots) - 1
        while first_okay > 6:
            if self.__cmp_n_back(first_okay, 1, result, hero_mem):
                first_okay -= 1
                continue
            rot_attempt = 0
            while not self.__cmp_n_back(first_okay, 5, result, hero_mem):
                if rot_attempt == first_okay:
                    first_okay -= 1
                    rot_attempt = 0
                slots_2 = result.copy()
                for i in range(first_okay):
                    result[i] = slots_2[(i + 1) % first_okay]
                rot_attempt += 1



        return result

    def get_hero_locations(self):
        begin = time.time()

        slots = []
        main_memory = []
        proc = join("/proc", str(self.PID))
        with open(join(proc, "maps")) as f:
            for line in f:
                _, max_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
        with open(join(proc, "maps")) as f:
            for line in f:
                heap_start, heap_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
                # if (heap_start > self.hero_location_neighbourhood + 0x1_000_000 or heap_end < self.hero_location_neighbourhood - 0x1_000_000) and \
                #     (heap_start > self.slots_location_neighbourhood + 0x2_000_000 or heap_end < self.slots_location_neighbourhood - 0x2_000_000):
                #     continue
                if heap_end - heap_start > 1_800_000_000:
                    continue

                try:

                    with self.rw_lock:
                        self.memory_file.seek(heap_start)
                        mem = self.memory_file.read(heap_end - heap_start)
                    self.hero_loader_progress = heap_start/max_end
                    # print(str(heap_end - heap_start).ljust(20), self.hero_loader_progress)


                    # if search(b"(Brissa)|(\x06\x00\x0b\x00.\x00\x75\x80)", mem, flags=MULTILINE | DOTALL):
                    for i in finditer(b"(\x06\x00\x0b\x00.\x00\x75\x80([\x00-\x08]{29}))", mem,
                                      flags=MULTILINE | DOTALL):
                        slots.append(i.span(2)[0] + heap_start)
                    # if heap_start > 0x6_000_000:
                    #     continue
                    for i in finditer(
                            b"((.)\x00{3}.{4}[\x00-\x07\xff]([A-Z][a-z]{2}[A-Z a-z\x00]{9}\x00)[\x00-\x15]\x00{3}(.).[\x00\xff]{1,3}.[\x00\xff]{1,3}[\x00\x01\xff][\x00\xff])",
                            mem, flags=MULTILINE | DOTALL):
                        if i.groups()[2].strip(b'\x00').decode().strip() not in consts.hero_names or \
                                consts.hero_ids[i.groups()[1][0]] != i.groups()[2].strip(b'\x00').decode():
                            continue
                        table_loc = i.span(3)[0]
                        if mem[table_loc + consts.secondary_skill_count] \
                            != sum((mem[table_loc+consts.secondary_skills+i] and 1)
                                   for i in range(consts.total_secondary_skill_count)):
                            continue
                        main_memory.append(
                            (i.groups()[2].strip(b'\x00').decode("ascii"), table_loc + heap_start))
                except IOError:
                    continue


        main_memory = [main_memory[i] for i in range(len(main_memory)) if i not in self.__resolve_duplicates(main_memory)]
        if len(main_memory) != len(slots) or len(slots) != 198:
            print(main_memory)
            print(set(consts.hero_ids) - set(i[0] for i in main_memory))
            self.hero_loader = FakeThread()
            raise IOError(f"Found {len(main_memory)} heroes and {len(slots)} slots")

        slots = self.__rotate_slots(slots, main_memory)

        # slots_2 = slots.copy()
        # for i in range(184):
        #     slots[i] = slots_2[(i + 21) % 184]
        #
        # slots_2 = slots.copy()
        # for i in range(163):
        #     slots[i] = slots_2[(i + 7) % 163]
        #
        # slots_2 = slots.copy()
        # for i in range(58):
        #     slots[i] = slots_2[(i + 31) % 58]

        self.mem_locations = {main_memory[i][0]: self.HeroLocation(main_memory[i][1], slots[i]) for i in
                              range(len(slots))}
        # for name, heroloc in self.mem_locations.items():
        #     print(str(consts.hero_ids.index(name)).rjust(5), name.ljust(20), self.dereference(heroloc.main+consts.secondary_skills, "B"*29), self.dereference(heroloc.slots, "B"*29))
        print("finished in", (time.time() - begin))

    def get_skills(self, name):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.secondary_skills)
            levels = self.memory_file.read(29)
            self.memory_file.seek(self.mem_locations[name].slots)
            slots = self.memory_file.read(29)

            for id, (slot, lvl) in enumerate(zip(slots, levels)):
                if lvl:
                    yield Skill(id, lvl, slot)

    def set_skills(self, name, skills):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            if len(skills) > 8:
                raise IndexError("Too many skills")

            if len({i.slot for i in skills}) != len(skills):
                raise IndexError("Doubled skill slot")

            self.memory_file.seek(self.mem_locations[name].main + consts.secondary_skills)
            self.memory_file.write(b'\x00' * 29)
            self.memory_file.seek(self.mem_locations[name].slots)
            self.memory_file.write(b'\x00' * 29)

            self.memory_file.seek(self.mem_locations[name].main + consts.secondary_skill_count)
            self.memory_file.write(len(skills).to_bytes(1, byteorder='little'))

            for skill in skills:
                self.memory_file.seek(self.mem_locations[name].main + consts.secondary_skills + skill.id)
                self.memory_file.write(skill.lvl.to_bytes(1, byteorder='little'))
                self.memory_file.seek(self.mem_locations[name].slots + skill.id)
                self.memory_file.write(skill.slot.to_bytes(1, byteorder='little'))

    def get_primary_skills(self, name):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.primary_skills)
            levels = self.memory_file.read(4)
            return list(levels)

    def set_primary_skills(self, name: str, levels: List[int]):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.primary_skills)
            self.memory_file.write(bytes(levels))

    def get_team(self, name):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.affiliation)
            return self.memory_file.read(1)[0]

    def get_troops(self, name):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.troop_id_array)
            ids = array('i')
            ids.frombytes(self.memory_file.read(ids.itemsize * 7))

            self.memory_file.seek(self.mem_locations[name].main + consts.troop_count_array)
            counts = array('i')
            counts.frombytes(self.memory_file.read(counts.itemsize * 7))

            return [Troop(id, amnt) for id, amnt in zip(ids, counts)]

    def set_troops(self, name: str, troops: List[Troop]):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            ids = array('i', [-1 for _ in range(7)])
            counts = array('i', [0 for _ in range(7)])

            for i, troop in enumerate(troops):
                ids[i] = troop.id
                counts[i] = troop.amount

            self.memory_file.seek(self.mem_locations[name].main + consts.troop_id_array)
            self.memory_file.write(ids.tobytes())

            self.memory_file.seek(self.mem_locations[name].main + consts.troop_count_array)
            self.memory_file.write(counts.tobytes())

    def set_location(self, name, x: int, y: int, underground: bool = False):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)
            if x is None:
                coords = array('h', [-1 for _ in range(3)])
            else:
                coords = array('h', [x, y, underground])
            self.memory_file.seek(self.mem_locations[name].main + consts.coordinates)
            self.memory_file.write(coords.tobytes())

    def get_location(self, name):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)
            coords = array('h')
            self.memory_file.seek(self.mem_locations[name].main + consts.coordinates)
            coords.frombytes(self.memory_file.read(coords.itemsize * 3))
            if coords[0] == -1:
                w = [None for _ in range(3)]
            else:
                w = coords.tolist()
                w[-1] = bool(w[-1])
            return w

    def dereference(self, address: int, format: str = "i"):
        with self.rw_lock:
            self.memory_file.seek(address)
            x = struct.unpack(format, self.memory_file.read(struct.calcsize(format)))
            if len(x) == 1:
                return x[0]
            else:
                return x

    def get_town(self, id: int):
        return Town(*self.dereference(self.town_array + 360 * id, consts.town_struct))

    def possess(self, name: str, original_team: int, team: int, x: int, y: int, underground: bool = False):
        if self.hero_loader.is_alive():
            return None
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)
            self.memory_file.seek(self.mem_locations[name].main + consts.affiliation)
            self.memory_file.write(team.to_bytes(1, byteorder='little'))

            self.memory_file.seek(self.mem_locations[name].main + consts.coordinates)
            self.memory_file.write(array("h", [x, y, underground]).tobytes())

    def get_tavern(self, color: int):
        return self.dereference(self.players_array + consts.player_tavern + color * 360, "ii")

    def get_safe_hero(self, n: int = 0) -> str | None:
        if self.hero_loader.is_alive():
            return None
        taken_heroes = set(consts.campaign_heroes)
        for i in range(8):
            taken_heroes |= set(self.get_player(i).heroes)
            taken_heroes |= set(self.get_tavern(i)) # TODO: delete after fixing hero finder
        safe_heroes = set(consts.hero_ids) - taken_heroes
        if self.hero_loader.is_alive():
            return list(safe_heroes)[n]
        # attempt to get a new hero
        for name in safe_heroes:
            if self.dereference(self.mem_locations[name].main + consts.xp_offset, "h") == 1:
                if n == 0:
                    return name
                n -= 1
        # pray there was no prison break
        for name in safe_heroes:
            if n == 0:
                return name
            n -= 1
        return None

    def set_tavern(self, color: int, tavern1: int, tavern2: int):
        offset = 0
        for player in (i for i in range(8) if i != color):
            safe = set(self.get_tavern(player)) - {tavern1, tavern2}
            for _ in range(2-len(safe)):
                safe.add(consts.hero_ids.index(self.get_safe_hero(offset)))
                offset += 1
            self.set_tavern_unsafe(player, *safe)
        self.set_tavern_unsafe(color, tavern1, tavern2)

    def set_tavern_unsafe(self, color: int, tavern1: int, tavern2: int):
        with self.rw_lock:
            self.memory_file.seek(self.players_array + consts.player_tavern + color * 360)
            self.memory_file.write(array("i", [tavern1, tavern2]).tobytes())



# 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00
# 06 00 0B 00 ?? 00 75 80

# Most Hero Stats
# FF FF FF FF FF FF 03 00 00 00 FF FF
