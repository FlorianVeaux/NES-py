from nes.cpu import CPU
from nes.ppu import PPU

class Console:
    def __init__(self):
        self.cpu = CPU(self)
        self.ppu = PPU(self)

    @staticmethod
    def create():
        return Console()
