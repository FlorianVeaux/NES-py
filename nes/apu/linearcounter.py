class LinearCounter:

    def __init__(self):
        self.control = False
        self.reload = False
        self.reload_value = 0x00
        self.counter = 0x00

    def reset(self):
        self.control = False
        self.reload = False
        self.reload_value = 0x00
        self.counter = 0x00

    def step(self):
        if self.reload:
            self.counter = self.reload_value
        elif self.counter > 0:
            self.counter -= 1

        # If the control flag is clear, the linear counter reload flag is cleared.
        if not self.control:
            self.reload = False

        return