from nes.apu.divider import Divider

class Sweep:
    def __init__(self):
        self.is_enabled = False
        self.reload = False
        self.divider = Divider()
        self.negative_flag = False
        self.shift = 0

    def reset(self):
        self.is_enabled = False
        self.reload = False
        self.divider = Divider()

    def step(self):
        """Returns true if pulse period needs to be adjusted"""
        return_value = False
        if self.reload:
            if self.divider.counter == 0 and self.is_enabled:
                return_value = True
            self.divider.reload()
            self.reload = False # Done reloading
        elif self.divider.step() and self.is_enabled:
            self.divider.reload()
            return_value = True

        return return_value