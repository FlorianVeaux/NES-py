from nes.apu.divider import Divider

class Envelope:
    def __init__(self):
        self.start = False
        self.loop = False
        self.divider = Divider()
        self.counter = 0x00 # 1 byte

    def reset(self):
        self.start = False
        self.loop = False
        self.divider.reset()
        self.counter = 0x00

    def step(self):
        if self.start:
            self.start = False
            self.counter = 0x0F
            self.divider.reload()
        elif self.divider.step():
            if self.counter > 0:
                self.counter = (self.counter - 1) & 0xFF
            elif self.loop:
                self.counter = 0x0F

