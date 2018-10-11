class FrameCounterError(Exception):
    pass


class FrameCounter:
    def __init__(self):
        self.register = 0x00
        self.step = 0x00
        self.cycles = 0
        self.mode = 4
        self.should_execute = False

    def reset(self):
        self.step = 0
        self.cycles = 0

    def read_register(self, address):
        if address == 0x4017:
            return self.register
        raise FrameCounterError("Cannot read register at address {0:04X}" % address)

    def write_register(self, address, value):
        if address == 0x4017:
            self.register = value
            self.reset()
            if self.mode == 5:
                self.should_execute = True
