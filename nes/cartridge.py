import numpy as np
import logging


log = logging.getLogger('nes.' + __name__)


class CartridgeError(Exception):
    """Base error class"""


class Cartridge:
    """A NES cartridge has at least two memory chips:
        - PRG (connected to CPU)
        - CHR (connected to PPU)
    There is at least a PRG ROM. The other components may, or may not be
    present.
    """
    def __init__(self, prg_rom, chr_rom=[],
                prg_ram_size=0,  chr_ram_size=0):
        self.prg_rom_size = len(prg_rom)
        self.chr_rom_size = len(chr_rom)
        self.prg_ram_size = prg_ram_size
        self.chr_ram_size = chr_ram_size
        self.PRG_ROM = prg_rom
        self.CHR_ROM = chr_rom
        if chr_ram_size:
            self.CHR_RAM = np.zeros(chr_ram_size, dtype='uint8')
        if prg_ram_size:
            self.PRG_RAM = np.zeros(prg_ram_size, dtype='uint8')

    def read_prg_rom(self, address):
        try:
            # Careful, this spams
            # log.debug(
            #     'PRG_ROM read: address=%s, value=%s', hex(address), self.PRG_ROM[address]
            # )
            return self.PRG_ROM[address]
        except IndexError:
            raise CartridgeError('Trying to read PRG_ROM at {}'.format(hex(address)))

    def read_chr_rom(self, address):
        try:
            return self.CHR_ROM[address]
        except IndexError:
            raise CartridgeError('Trying to read CHR_ROM at {}'.format(hex(address)))

    def read_chr_ram(self, address):
        try:
            return self.CHR_RAM[address]
        except IndexError:
            raise CartridgeError('Trying to read CHR_RAM at {}'.format(hex(address)))

    def read_prg_ram(self, address):
        try:
            return self.PRG_RAM[address]
        except IndexError:
            raise CartridgeError('Trying to read PRG_RAM at {}'.format(hex(address)))

    def write_prg_ram(self, address, value):
        try:
            self.PRG_RAM[address] = value
        except IndexError:
            raise CartridgeError("Trying to write PRG_RAM at {}".format(hex(address)))

    def write_chr_rom(self, address, value):
        try:
            self.CHR_ROM[address] = value
        except IndexError:
            raise CartridgeError("Trying to write CHR_ROM at {}".format(hex(address)))
