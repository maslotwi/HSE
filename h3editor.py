import subprocess
import consts
from dataclasses import dataclass
from os.path import join
from re import search, MULTILINE, finditer, DOTALL
from typing import List
from array import array


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


class H3editor:
    @dataclass(frozen=True, order=True)
    class HeroLocation:
        main: int
        slots: int

    def __init__(self, process_name="h3hota HD.exe"):
        self.process_name = process_name
        self.PID = None
        self.memory_file = None
        self.mem_locations = None
        self.get_PID()

        if self.PID is not None:
            self.open_memory_file()
            self.get_hero_locations()
            self.get_player_locations('Player2', 'Computer')

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


    def get_player_locations(self, second_to_last: str, last: str):
        proc = join("/proc", str(self.PID))
        last_player = None
        with open(join(proc, "maps")) as f:
            for line in f:
                heap_start, heap_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
                if not line.strip().startswith("0") or heap_start > 0x7_000_000:
                    continue
                try:

                    self.memory_file.seek(heap_start)
                    mem = self.memory_file.read(heap_end - heap_start)
                    if search(f'({second_to_last})|({last})'.encode(), mem, flags=MULTILINE | DOTALL):
                        for i in finditer(f"((?<=({second_to_last}).{{{360-len(second_to_last)}}}){last})".encode(), mem,
                                          flags=MULTILINE | DOTALL):
                            last_player = i.start()+heap_start
                            print(last_player)

                except IOError:
                    continue
        self.players_array = last_player - 7 * 360

    def get_player(self, color: int):
        self.memory_file.seek(self.players_array + consts.player_heroes + color * 360)
        hero_array = array('I')
        hero_array.frombytes(self.memory_file.read(4*8))
        hero_array = [consts.hero_ids[i] for i in hero_array if i < 256]

        self.memory_file.seek(self.players_array + consts.player_resources + color * 360)
        resource_array = array('i')
        resource_array.frombytes(self.memory_file.read(4*7))

        self.memory_file.seek(self.players_array + color * 360)
        name = self.memory_file.read(21)
        try:
            name = name[:name.index(b"\x00")].decode("ascii")
        except UnicodeDecodeError:
            print(name)
        return Player(color, hero_array, name, resource_array.tolist())


    def get_hero_locations(self):
        slots = []
        main_memory = []
        proc = join("/proc", str(self.PID))

        with open(join(proc, "maps")) as f:
            for line in f:
                heap_start, heap_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
                if not line.strip().startswith("0") or heap_start > 0x5_000_000 or heap_end < 0x3_000_000:
                    continue
                try:
                    self.memory_file.seek(heap_start)
                    mem = self.memory_file.read(heap_end - heap_start)
                    if search(b"(Brissa)|(\x06\x00\x0b\x00.\x00\x75\x80)", mem, flags=MULTILINE | DOTALL):
                        for i in finditer(b"(\x06\x00\x0b\x00.\x00\x75\x80([\x00-\x08]{29}))", mem,
                                          flags=MULTILINE | DOTALL):
                            slots.append(i.span(2)[0] + heap_start)
                        for i in finditer(
                                b"([\x00-\x07\xff]([A-Z][a-z]{2}[A-Z a-z\x00]{9}\x00)[\x00-\x15]\x00{3}(.).[\x00\xff]{1,3}.[\x00\xff]{1,3}[\x00\x01\xff][\x00\xff])",
                                mem, flags=MULTILINE | DOTALL):
                            if i.groups()[1].strip(b'\x00').decode().strip() not in consts.hero_names:
                                continue
                            main_memory.append(
                                (i.groups()[1].strip(b'\x00').decode("ascii"), i.span(2)[0] + heap_start))
                except IOError:
                    continue
        if len(main_memory) != len(slots) or len(slots) != 198:
            self.memory_file.seek(0x4d75a90)
            dane = self.memory_file.read(30)

            print(main_memory)
            print(set(consts.hero_ids)-set(i[0] for i in main_memory))

            raise IOError(f"Found {len(main_memory)} heroes and {len(slots)} slots")
        slots_2 = slots.copy()
        for i in range(162):
            slots[i] = slots_2[(i+6)%162]
        self.mem_locations = {main_memory[i][0]: self.HeroLocation(main_memory[i][1], slots[i]) for i in
                              range(len(slots))}

    def get_skills(self, name):
        if name not in self.mem_locations:
            raise KeyError(name)

        self.memory_file.seek(self.mem_locations[name].main + consts.secondary_skills)
        levels = self.memory_file.read(29)
        self.memory_file.seek(self.mem_locations[name].slots)
        slots = self.memory_file.read(29)

        for id, (slot, lvl) in enumerate(zip(slots, levels)):
            if lvl:
                yield Skill(id, lvl, slot)

    def get_team(self, name):
        if name not in self.mem_locations:
            raise KeyError(name)

        self.memory_file.seek(self.mem_locations[name].main + consts.affiliation)
        return self.memory_file.read(1)[0]

    def set_skills(self, name, skills):
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

# 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00
# 06 00 0B 00 ?? 00 75 80

# Most Hero Stats
# FF FF FF FF FF FF 03 00 00 00 FF FF
