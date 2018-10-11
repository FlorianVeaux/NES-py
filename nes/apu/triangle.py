from nes.apu.divider import Divider
from nes.apu.linearcounter import LinearCounter
from nes.apu.sequencer import Sequencer

class TriangleError(Exception):
    pass

class Triangle:

    LENGTH_COUNTER_DATA = [
        10 , 254, 20, 2 ,
        40 , 4  , 80, 6 ,
        160, 8  , 60, 10,
        14 , 12 , 26, 14,
        12 , 16 , 24, 18,
        48 , 20 , 96, 22,
        192, 24 , 72, 26,
        16 , 28 , 32, 30
    ]

    def __init__(self):
        self.divider = Divider()
        self.length_counter = 0x00
        self.linear_counter = LinearCounter()
        self.sequencer = Sequencer()

        self.is_enabled = False
        self.registers = [0x00, 0x00, 0x00]

    def reset(self):
        self.is_enabled = False
        self.registers = [0x00, 0x00, 0x00]
        self.divider.reset()
        self.length_counter = 0x00
        self.linear_counter.reset()
        self.sequencer.reset()

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False
        self.length_counter = 0x00

    def read_register(self, address):
        if address == 0x4008:
            return self.registers[0]
        elif address == 0x400A:
            return self.registers[1]
        elif address == 0x400B:
            return self.registers[2]
        else:
            raise TriangleError("Invalid read access to register {}".format(hex(address)))

    def write_register(self, address, value):
        if address == 0x4008:
            # CRRR.RRRR, control flag + counter reload value
            self.registers[0] = value
            self.linear_counter.control = value >> 7
            self.linear_counter.reload_value = value & 0x7F
        elif address == 0x400A:
            # LLLL.LLLL, timer low
            self.registers[1] = value
            self.divider.period = (self.divider.period & 0x0700) | value
        elif address == 0x400B:
            # llll.lHHH, length counter load and timer high
            self.registers[2] = value
            if self.is_enabled:
                self.length_counter = self.LENGTH_COUNTER_DATA[value >> 3]
            self.divider.period = (self.divider.period & 0x00FF) | ((value >> 3) << 8)
            self.linear_counter.reload = True
        else:
            raise TriangleError("Invalid write access to register {}".format(hex(address)))

    def output(self):
        if not self.is_enabled:
            return 0
        if self.linear_counter == 0:
            return 0
        if self.length_counter == 0:
            return 0
        return self.sequencer.output_value
