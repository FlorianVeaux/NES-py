from nes.apu import APU
from nes.cpu import CPU
from nes.ppu import PPU
from nes.mapper import Mapper

class Console:
    def __init__(self, file_name):
        self.cpu = CPU(self)
        self.ppu = PPU(self)
        self.apu = APU(self)
        self.mapper = Mapper.from_nes_file(file_name)

    def step(self):
        cpu_steps = self.cpu.step()
        ppu_steps = 3*cpu_steps # 3.2 pour PAL
        for _ in range(ppu_steps):
            self.ppu.step()

        for _ in range(cpu_steps):
            self.apu.step()

        return cpu_steps
