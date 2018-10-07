from nes.cpu import CPU
from nes.ppu import PPU

class Console:
    def __init__(self):
        self.cpu = CPU(self)
        self.ppu = PPU(self)

    def load_cartridge(self, cartridge):
        """Binds a Cartridge object to the console.
        """
        self.cartridge = cartridge

    @staticmethod
    def create():
        return Console()
