class Divider:
    def __init__(self):
        self.counter = 0x00
        self.period = 0x00

    def reset(self):
        self.counter = 0x00
        self.period = 0x00

    def reload(self):
        self.counter = self.period

    def step(self):
        self.counter = (self.counter - 1) & 0xFFFF
        if self.counter == 0:
            self.reload()
            return True
        return False
