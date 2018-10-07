import numpy as np
from nes.utility import parse_nes_file

class CartridgeError(Exception):
    """Base error class"""


class Cartridge:
    """A NES cartridge has at least two memory chips:
        - PRG (connected to CPU)
        - CHR (connected to PPU)
    There is at least a PRG ROM. The other components may, or may not be
    present.
    """
    def __init__(self, prg_rom, chr_rom=None,
                prg_ram_size=0,  chr_ram_size=0):
        self.PRG_ROM = prg_rom
        if chr_rom:
            self.CHR_ROM = chr_rom
        if chr_ram_size:
            self.CHR_RAM = np.zeros(chr_ram_size, dtype='uint8')
        if prg_ram_size:
            self.PRG_RAM = np.zeros(prg_ram_size, dtype='uint8')

    def read_rom(address):
        try:
            return self.PRG_ROM[address]
        except IndexError:
            raise CartridgeError('Trying to read PRG_ROM at {}'.format(hex(address)))


    @staticmethod
    def from_nes_file(nesfile):
        """Creates a cartridge from an iNES file. For format info, see
        https://wiki.nesdev.com/w/index.php/INES.
        """
        with open(nesfile, 'rb') as f:
            prg_rom, chr_rom, prg_ram_size, chr_ram_size = parse_nes_file(f)

        return Cartridge(
            prg_rom, chr_rom, prg_ram_size, chr_ram_size
        )
