import numpy as np
import pdb

class CPUMemory(object):
    """CPU Memory structure:
        $0000
            2kb RAM, mirrored 4 times
        $2000
            Access to PPU I/O registers (8 of them, mirrored all accross)
        $4000
            ??? (at least access to some OAM related I/O)
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
        # TODO: shouldn't it be 'if address < 0x2000' ? see docstring
        if 0x800 <= address < 0x2000:
            print("Hello")
            print(address)
            address %= 0x800
        elif address < 0x4000:
            # PPU registers are mirrored every 8 bytes
            # e.g. address 0x3210 => 0x3210 % 8 = 0 => read 0x2000
            self._console.ppu.read_register(0x2000 + address % 8)

        return self._memory[address]

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


