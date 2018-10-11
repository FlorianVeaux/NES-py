from nes.apu.divider import Divider
from nes.apu.envelope import Envelope


class NoiseError(Exception):
    pass

class Noise:

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

    PERIOD_DATA = [
        4, 8, 16, 32, 64, 96, 128, 160, 202,
		254, 380, 508, 762, 1016, 2034, 4068,
    ]

    def __init__(self):
        self.envelope = Envelope()
        self.divider = Divider()
        self.shift = 0x0000
        self.length_counter = 0x00
        self.is_enabled = False
        self.registers = [0x00, 0x00, 0x00]

    def reset(self):
        self.is_enabled = False
        self.registers = [0x00, 0x00, 0x00]
        self.divider.reset()
        self.length_counter = 0x00
        self.envelope.reset()
        self.shift = 0x0000

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False
        self.length_counter = 0x00

    def read_register(self, address):
        if address == 0x400c:
            return self.registers[0]
        elif address == 0x400e:
            return self.registers[1]
        elif address == 0x400f:
            return self.registers[2]
        else:
            raise NoiseError("Invalid read access to register {}".format(hex(address)))

    def write_register(self, address, value):
        if address == 0x400c:
            # --lc.vvvv, length counter halt, constant volume/envelope flag, volume/envelope divider period
            self.registers[0] = value
            self.envelope.loop = ((value >> 5) & 1) == 1
            self.envelope.divider.period = value & 0x0F
        elif address == 0x400e:
            # M---.PPPP Mode, period
            self.registers[1] = value
            self.divider.period = self.PERIOD_DATA[value & 0x0F]
            self.divider.reload()
        elif address == 0x400F:
            # llll.l--- Length counter load and envelope restart
            self.registers[2] = value
            self.envelope.start = True
            if self.is_enabled:
                self.length_counter = self.LENGTH_COUNTER_DATA[value >> 3]
        else:
            raise NoiseError("Invalid write access to register {}".format(hex(address)))

    def output(self):
        if not self.is_enabled:
            return 0
        if self.shift & 0x0001 != 0:
            return 0
        if self.length_counter == 0:
            return 0
        if (self.registers[0] >> 4) & 0x01: # Constant volume flag
            return self.envelope.counter
        else:
            return self.registers[0] & 0x0F
