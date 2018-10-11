from nes.apu.divider import Divider
from nes.apu.envelope import Envelope
from nes.apu.sequencer import Sequencer
from nes.apu.sweep import Sweep
class PulseError(Exception):
    pass

class Pulse:

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

    SEQUENCER_DATA = [
        [0b0, 0b1, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0],
        [0b0, 0b1, 0b1, 0b0, 0b0, 0b0, 0b0, 0b0],
        [0b0, 0b1, 0b1, 0b1, 0b1, 0b0, 0b0, 0b0],
        [0b1, 0b0, 0b0, 0b1, 0b1, 0b1, 0b1, 0b1]
    ]

    def __init__(self):
        self.divider = Divider()
        self.envelope = Envelope()
        self.sequencer = Sequencer()
        self.sweep = Sweep()
        self.length_counter = 0x00

        self.is_enabled = False

        # Used with Pulse1 for negative updates of the period
        # The period is decreased by one more unit
        self.period_minus_one = False
        self.registers = [0x00, 0x00, 0x00, 0x00]

    def reset(self):
        self.is_enabled = False
        self.registers = [0x00, 0x00, 0x00, 0x00]
        self.divider.reset()
        self.envelope.reset()
        self.sequencer.reset()
        self.sweep.reset()
        self.length_counter = 0x00

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False
        self.length_counter = 0x00

    def read_register(self, address):
        if 0x4000 <= address < 0x4004:
            return self.registers[address - 0x4000]
        elif 0x4004 <= address < 0x4008:
            return self.registers[address - 0x4004]
        else:
            raise PulseError("Invalid read access to register {}".format(hex(address)))

    def write_register(self, address, value):
        if address == 0x4000 or address == 0x4004:
            # CONTROL register
            self.registers[0] = value
            self.envelope.counter = value & 0x0F
            self.envelope.loop = (value >> 5) & 0x01 == 1
            self.sequencer.values = self.SEQUENCER_DATA[value >> 6]
        elif address == 0x4001 or address == 0x4005:
            # SWEEP register
            self.registers[1] = value
            # EPPPNSSS
            self.sweep.is_enabled = value >> 7 == 1 # E
            self.sweep.divider.period = (value >> 4) & 0b111 # PPP
            self.sweep.negative_flag = (value >> 3) & 0x01 # N
            self.sweep.shift = (value & 0x07) # SSS
            self.sweep.reload = True
        elif address == 0x4002 or address == 0x4006:
            # TIMER LOW register
            self.registers[2] = value
            self.divider.period = (self.divider.period & 0x0700) | value
        elif address == 0x4003 or address == 0x4007:
            self.registers[3] = value
            if self.is_enabled:
                self.length_counter = self.LENGTH_COUNTER_DATA[value >> 3]
            self.divider.period = (self.divider.period & 0x00FF) | ((value & 0x07) << 8)
            self.sequencer.reset()
            self.envelope.start = True
        else:
            raise PulseError("Invalid write access to register {}".format(hex(address)))

    def get_period(self):
        """The sweep unit continuously calculates each channel's target period in this way:
        - A barrel shifter shifts the channel's 11-bit raw timer period right by the shift count, producing the change amount.
        - If the negate flag is true, the change amount is made negative.
        - The target period is the sum of the current period and the change amount.
        """
        current_period = self.divider.period
        sweep_shift = self.sweep.shift
        diff = current_period >> sweep_shift

        """The two pulse channels have their adders' carry inputs wired differently,
        which produces different results when each channel's change amount is made negative:
        - Pulse 1 adds the ones' complement (−c − 1). Making 20 negative produces a change amount of −21.
        - Pulse 2 adds the two's complement (−c). Making 20 negative produces a change amount of −20.
        """
        if self.sweep.negative_flag:
            diff = -diff
            if self.period_minus_one:
                diff -= 1

        return current_period + diff

    def output(self):
        """The mixer receives the current envelope volume except when
        - The sequencer output is zero, or
        - overflow from the sweep unit's adder is silencing the channel, or
        - the length counter is zero, or
        - the timer has a value less than eight."""
        if self.sequencer.output_value == 0:
            return 0
        if self.divider.period < 8 or self.get_period() > 0x07FF:
            return 0
        if self.length_counter == 0:
            return 0

        if (self.registers[0] >> 4) & 1: # Constant Volume
            return self.envelope.counter
        else:
            return self.registers[0] & 0x0F

