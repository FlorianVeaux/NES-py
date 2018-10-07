from nes.cpu import CPU
from nes.ppu import PPU

class Console:
    def __init__(self):
        self.cpu = CPU(self)
        self.ppu = PPU(self)

    def load_cartridge(self, mapper):
        """Binds a cartridge and its mapper to the console.
        """
        self.mapper = mapper
        self.cpu.reset()

    @staticmethod
    def create():
        return Console()
