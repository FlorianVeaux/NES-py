import numpy as np
import pdb

from nes.mirror import mirrored_address


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
        self._RAM = np.zeros(CPUMemory.RAM_SIZE, dtype='uint8')
        self._console = console

    def reset(self):
        self._RAM = np.zeros(CPUMemory.RAM_SIZE, dtype='uint8')

    def read(self, address):
        if address < 0x2000:
            # 2kb, mirrored 4 times
            return self._RAM[address % 0x800]
        elif address < 0x4000:
            # PPU registers are mirrored every 8 bytes
            # e.g. address 0x3210 => 0x3210 % 8 = 0 => read 0x2000
            return self._console.ppu.read_register(0x2000 + address % 8)
        elif address < 0x5000:
            # TODO: implement
            raise NotImplementedError(
                'Read not implemented at address={}'.format(hex(address))
            )
        elif address < 0x6000:
            # TODO: implement expansion modules
            raise NotImplementedError(
                'Read not implemented at address={}'.format(hex(address))
            )
        elif address < 0x10000:
            return self._console.mapper.read_prg(address)
        else:
            raise CPUMemoryError('Unknown address: {}'.format(hex(address)))

    def write(self, address, value):
        if address < 0x2000:
            self._RAM[address % 0x800] = value
        else:
            # TODO: implement various writes
            raise NotImplementedError(
                'CPU write not implemented at address={}'.format(hex(address))
            )

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
        self._palette = np.zeros(PPUMemory._PALETTE_SIZE, dtype='uint8')
        self._name_table = np.zeros(PPUMemory.NAME_TABLE_SIZE, dtype='uint8')

    def read(self, address):
        if address < 0x2000:
            return self._console.mapper.read_chr(address)
        elif address < 0x3000:
            mirroring = self._console.mapper.mirror_id
            return self._name_table[mirrored_address(address, mirroring) - 0x2000]
        elif 0x3F00 <= address < 0x3F20:
            return self._palette[address - 0x3F00]
        else:
            raise PPUMemoryError('Unknown address: {}'.format(hex(address)))

    def write(self, address, value):
        raise NotImplementedError(
            'PPU write not implemented at address={}'.format(hex(address))
        )