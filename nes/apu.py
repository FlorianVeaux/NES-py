import numpy as np

class APUError(Exception):
    pass

class Pulse:
    pass

class Triangle:
    pass

class Noise:
    pass

class DMC:
    pass

class APU:

    def __init__(self, console):
        self.registers = np.zeros(24, dtype='uint8')
        self.status = 0x00
        self.frame_counter = 0x00
        self.console = console

    def read_register(self, address):
        if address == 0x4015:
            return self.registers[0x15]
        else:
            raise APUError("Operation read not allowed at address={}".format(address))

    def write_register(self, address, value):
        if address <= 0x4017 and address not in [0x4009, 0x400D, 0x4014]:
            self.registers[address - 0x4000] = value
        else:
            raise APUError("Operation write not allowed at address={}".format(address))

