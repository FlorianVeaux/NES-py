import numpy as np
import pdb

class MemError(Exception):
    """Base error class"""


class CPUMemoryError(MemError):
    """Raise on CPUMemory Error"""


class CPUMemory(object):
    """CPU Memory structure:
        $0000
            2kb RAM, mirrored 4 times
        $2000
            Access to PPU I/O registers (8 of them, mirrored all accross)
        $4000
            $4014 ppu OAMDMA register
            $4016 left joystick
            $4017 right joystick
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
    MEM_SIZE = 65536

    def __init__(self, console):
        self._memory = np.zeros(CPUMemory.MEM_SIZE, dtype='uint8')
        self._console = console

    def reset(self):
        self._memory = np.zeros(CPUMemory.MEM_SIZE, dtype='uint8')

    def read(self, address):
        if 0x800 <= address < 0x2000:
            # 2kb, mirrored 4 times
            return self._memory[address % 0x800]
            address %= 0x800
        elif address < 0x4000:
            # PPU registers are mirrored every 8 bytes
            # e.g. address 0x3210 => 0x3210 % 8 = 0 => read 0x2000
            return self._console.ppu.read_register(0x2000 + address % 8)
        elif address < 0x10000:
            # TODO: implement
            raise NotImplementedError(
                'Read not implemented at address={}'.format(hex(address))
            )
        else:
            raise CPUMemoryError('Unknown address: {}'.format(hex(address)))

    def write(self, address, value):
        if 0x800 <= address < 0x2000:
            address %= 0x800
        self._memory[address] = value

    def load_ROM(self, initAddress, values):
        endAddress = min(initAddress+values.size, self.MEM_SIZE)
        self._memory[initAddress:endAddress] = values[0:endAddress - initAddress]

    @staticmethod
    def get_stack_address(address):
        return 0x1A0 | address


