class Sequencer:
    def __init__(self):
        self.values = [] # byte array
        self.current_index = 0
        self.output_value = 0

    def reset(self):
        self.current_index = 0
        self.output_value = 0

    def step(self):
        if not self.values:
            return

        self.output_value = self.values[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.values)