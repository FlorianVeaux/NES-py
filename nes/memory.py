import numpy as np
import pdb
import logging

from nes.mirror import mirrored_address


log = logging.getLogger('nes.' + __name__)


class MemError(Exception):
    """Base error class"""

class CPUMemoryError(MemError):
    """Raise on CPUMemory Error"""

class PPUMemoryError(MemError):
    """Raise on PPUMemory Error"""


class CPUMemory(object):
    """CPU Memory structure:
        $0000
            2kb RAM, mirrored 4 times
        $2000
            Access to PPU I/O registers (8 of them, mirrored all accross)
        $4000
            $4000 - $4013: APU register
            $4014 ppu OAMDMA register
            $4015 APU register
            $4016 left joystick (this demands source checking...)
            $4017 right joystick (also APU??)
            ??? (other stuff maybe?)
        $5000
            Expansion modules
        $6000
            PRG RAM
        $8000
            PRG ROM (lower)
        $C000
            PRG ROM (upper)
        $10000
    """
    RAM_SIZE = 0x0800

    def __init__(self, console):
        self._RAM = np.zeros(CPUMemory.RAM_SIZE, dtype='int')
        self._console = console

    def reset(self):
        self._RAM = np.zeros(CPUMemory.RAM_SIZE, dtype='int')

    def read(self, address):
        if address <= 0x1FFF:
            # 2kb, mirrored 4 times
            return self._RAM[address % 0x800]
        elif address <= 0x3FFF:
            # PPU registers are mirrored every 8 bytes
            # e.g. address 0x3210 => 0x3210 % 8 = 0 => read 0x2000
            return self._console.ppu.read_register(0x2000 + address % 8)
        elif address == 0x4014:
            return self._console.ppu.read_register(address)
        elif address <= 0x4FFF:
            return self._console.apu.read_register(address)
        elif address <= 0x5FFF:
            # TODO: implement expansion modules
            raise NotImplementedError(
                'Read not implemented at address={}'.format(hex(address))
            )
        elif address <= 0xFFFF:
            return self._console.mapper.read_prg(address)
        else:
            raise CPUMemoryError('Unknown address: {}'.format(hex(address)))

    def read_page(self, address):
        if address <= 0x1F:
            address_begin = (address % 0x800) << 8
            address_end = address_begin | 0x00FF
            data = self._RAM[address_begin:address_end + 1]
            return data
        elif address <= 0x3F:
            raise NotImplementedError(
                'You should not read a page of PPU registers'
            )
        elif address <= 0x4F:
            raise NotImplementedError(
                'You should not read a page at address={}'.format(hex(address))
            )
        elif address <= 0x5F:
            raise NotImplementedError(
                'You should not read a page at address={}'.format(hex(address))
            )
        elif address <= 0xFF:
            raise NotImplementedError(
                'We need a way to batch read from the cartdrige at address={}'.format(hex(address))
            )
        else:
            raise NotImplementedError(
                'You should not read a page at address={}'.format(hex(address))
            )



    def write(self, address, value):
        if address < 0x2000:
            self._RAM[address % 0x800] = value
        elif address < 0x4000:
            # PPU registers are mirrored every 8 bytes
            # e.g. address 0x3210 => 0x3210 % 8 = 0 => write 0x2000
            self._console.ppu.write_register(0x2000 + address % 8, value)
        elif address == 0x4014:
            self._console.ppu.write_register(address, value)
        elif address < 0x5000:
            self._console.apu.write_register(address, value)
        elif address < 0x6000:
            # TODO: implement expansion modules
            raise NotImplementedError(
                'Read not implemented at address={}'.format(hex(address))
            )
        elif address < 0x10000:
            self._console.mapper.write_prg(address, value)
        else:
            raise CPUMemoryError('Unknown address: {}'.format(hex(address)))

    @staticmethod
    def get_stack_address(address):
        return 0x1A0 | address


class PPUMemory:
    """PPU Memory structure:
    $0000
        Pattern table (256 * 8 * 2) * 2 (In cartridge)
    $2000
        (Name table (30 * 32) + Attribut table (64)) * 4
    $3000
        Empty
    $3F00
        Image Palette
    $3F10
        Sprite Palette
    $3F20
        Empty
    $4000
    """
    # Includes both sprite and image palette
    PALETTE_SIZE = 0x0020
    NAME_TABLE_SIZE = 0x1000

    def __init__(self, console):
        self._console =  console
        self._palette = np.zeros(PPUMemory.PALETTE_SIZE, dtype='int')
        self._name_table = np.zeros(PPUMemory.NAME_TABLE_SIZE, dtype='int')

    def read(self, address):
        if address < 0x2000:
            return self._console.mapper.read_chr(address)
        elif address < 0x3000:
            mirroring = self._console.mapper.mirror_id
            return self._name_table[mirrored_address(address, mirroring) - 0x2000]
        elif 0x3F00 <= address < 0x4000:
            pointer = address % 32
            if pointer >= 16 and pointer % 4 == 0:
                pointer -= 16
            return self._palette[pointer]
        else:
            raise PPUMemoryError('Unknown address: {}'.format(hex(address)))

    def write(self, address, value):
        if address < 0x2000:
            self._console.mapper.write_chr(address, value)
        elif address < 0x3000:
            mirroring = self._console.mapper.mirror_id
            self._name_table[mirrored_address(address, mirroring) - 0x2000] = value
        elif 0x3F00 <= address < 0x4000:
            pointer = address % 32
            if pointer >= 16 and pointer % 4 == 0:
                pointer -= 16
            self._palette[pointer] = value
        else:
            raise PPUMemoryError('Unknown address: {}'.format(hex(address)))
