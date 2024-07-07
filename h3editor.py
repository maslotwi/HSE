import subprocess
from os.path import join
from re import match, MULTILINE, finditer, DOTALL
class ProcessNotFound(Exception):
    pass


class H3editor:
    def __init__(self, process_name="h3hota HD.exe"):
        self.process_name = process_name
        self.PID = None
        self.get_PID()

    def validate_hero(self):
        ...

    def get_PID(self):
        try:
            pid = subprocess.check_output(["pgrep", "-o", self.process_name])
            self.PID = int(pid)
        except subprocess.CalledProcessError:
            self.PID = None

    def open_memory(self):
        L = 0
        with open("test.bin", "w"):
            ...
        self.get_PID()
        if self.PID is None:
            raise ProcessNotFound("Could not find Heroes 3 process")
        proc = join("/proc", str(self.PID))
        heap_start, heap_end = None, None
        with open(join(proc, "maps")) as f:
            for line in f:
                #if line.startswith("04d40000-05540000"):
                heap_start, heap_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
                _, heap_end = map(lambda x: int(x, base=16), line.split()[0].split('-'))
                # if heap_start_new != heap_end:
                #     heap_end

                try:
                    with open(join(proc, "mem"), "rb+") as f:
                        f.seek(heap_start)
                        mem = f.read(heap_end - heap_start)
                        if mem.find(b"Brissa") != -1 or match(b"\x06\x00\x0b\x00.\x00\x75\x80", mem, flags=MULTILINE | DOTALL):
                            print(line)
                            for i in finditer(b"\x06\x00\x0b\x00.\x00\x75\x80", mem, flags=MULTILINE | DOTALL):
                                print(i)
                                L+=1
                            with open("test.bin", "ab") as f2:
                                f2.write(mem)
                except Exception:
                    continue
            #print(mem)
        print(L)
# 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00
# 06 00 0B 00 ?? 00 75 80
