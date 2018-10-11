from nes.apu.apu import APU
from nes.cpu import CPU
from nes.ppu import PPU
from nes.mapper import Mapper

class Console:
    def __init__(self, file_name, screen=None, debug=False):
        self._debug = debug
        if debug:
            self.debugger = Debugger()
        self.cpu = CPU(self)
        self.ppu = PPU(self)
        self.apu = APU(self)
        self.screen = screen
        self.mapper = Mapper.from_nes_file(file_name)
        self.cpu.reset()
        self.ppu.reset()

    def step(self):
        cpu_steps = self.cpu.step(self._debug)
        ppu_steps = 3*cpu_steps # 3.2 pour PAL
        for _ in range(ppu_steps):
            self.ppu.step()

        # for _ in range(cpu_steps):
        #     self.apu.step()

        return cpu_steps


class Debugger:
    def __init__(self):
        self.data = []
        self.pixel_data = []

    def log_data(self, debug_data):
        s = debug_data['PC'] + "  "
        s += debug_data['opcode'] + " "
        for arg in debug_data['args']:
            s+= arg + " "
        s = s.ljust(15)
        s += debug_data['mneumonic']
        s = s.ljust(48)
        s += debug_data['A'] + " " + debug_data['X'] + " " + debug_data['Y'] + " " + debug_data['P'] + " "
        s += debug_data['SP'] + " "
        # cyc_s= str(self.step_cycles% 341).rjust(3)
        # s+= "CYC:{}".format(cyc_string)
        self.data.append(s)

    def log_str(self, s):
        self.data.append(s)

    def log_pix(self, s, x, y):
        print(x, y)
        s = str(s) + ' '
        if y == 0 and x == 0:
            self.pixel_data.append('NEW FRAME\n')
        if x == 0:
            self.pixel_data.append(s)
        else:
            self.pixel_data[y] += s

    def dump(self, file_path):
        print('logging to {}'.format(file_path))
        with open(file_path, 'w') as f:
            f.write('\n'.join(self.data))
