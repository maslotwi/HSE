import struct
import subprocess
import consts
import collections
from dataclasses import dataclass
from os.path import join
from re import search, MULTILINE, finditer, DOTALL
from typing import List
from array import array
from threading import Lock


class ProcessNotFound(Exception):
    pass


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
        self.hero_location_neighbourhood = None
        self.process_name = process_name
        self.rw_lock = Lock()
        self.PID = None
        self.memory_file = None
        self.mem_locations = None
        self.reload()

    def reload(self):
        self.get_PID()
        if self.PID is not None:
            self.open_memory_file()
            with self.rw_lock:
                with open("cache") as f:
                    data = f.read().splitlines()
                    self.hero_location_neighbourhood = int(data[0], base=16)
                    self.slots_location_neighbourhood = int(data[1], base=16)
                self.get_hero_locations()
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

    def get_hero_locations(self):
        slots = []
        main_memory = []
        proc = join("/proc", str(self.PID))

        with (open(join(proc, "maps")) as f):
            for line in f:
                heap_start, heap_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
                if (heap_start > self.hero_location_neighbourhood + 0x1_000_000 or heap_end < self.hero_location_neighbourhood - 0x1_000_000) and \
                    (heap_start > self.slots_location_neighbourhood + 0x2_000_000 or heap_end < self.slots_location_neighbourhood - 0x2_000_000):
                    continue


                try:
                    self.memory_file.seek(heap_start)
                    mem = self.memory_file.read(heap_end - heap_start)

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
                        main_memory.append(
                            (i.groups()[2].strip(b'\x00').decode("ascii"), i.span(3)[0] + heap_start))
                except IOError:
                    continue
        if len(main_memory) != len(slots) or len(slots) != 198:
            print(main_memory)
            print(set(consts.hero_ids) - set(i[0] for i in main_memory))

            raise IOError(f"Found {len(main_memory)} heroes and {len(slots)} slots")
        slots_2 = slots.copy()
        for i in range(163):
            slots[i] = slots_2[(i - 156) % 163]

        self.mem_locations = {main_memory[i][0]: self.HeroLocation(main_memory[i][1], slots[i]) for i in
                              range(len(slots))}

    def get_skills(self, name):
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
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.primary_skills)
            levels = self.memory_file.read(4)
            return list(levels)

    def set_primary_skills(self, name: str, levels: List[int]):
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.primary_skills)
            self.memory_file.write(bytes(levels))

    def get_team(self, name):
        with self.rw_lock:
            if name not in self.mem_locations:
                raise KeyError(name)

            self.memory_file.seek(self.mem_locations[name].main + consts.affiliation)
            return self.memory_file.read(1)[0]

    def get_troops(self, name):
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
        taken_heroes = set(consts.campaign_heroes)
        for i in range(8):
            taken_heroes |= set(self.get_player(i).heroes)
        safe_heroes = set(consts.hero_ids) - taken_heroes

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
