from nes.apu.divider import Divider

class DMCError(Exception):
    pass

class DMC:
    """Not implemented yet"""

    def __init__(self):
        self.registers = [0x00, 0x00, 0x00, 0x00]

    def read_register(self, address):
        if address == 0x4010:
            return self.registers[0]
        elif address == 0x4011:
            return self.registers[1]
        elif address == 0x4012:
            return self.registers[2]
        elif address == 0x4013:
            return self.registers[3]
        else:
            raise DMCError("Invalid read access to register {}".format(hex(address)))

    def write_register(self, address, value):
        if address == 0x4010:
            self.registers[0] = value
        elif address == 0x4011:
            self.registers[1] = value
        elif address == 0x4012:
            self.registers[2] = value
        elif address == 0x4013:
            self.registers[3] = value
        else:
            raise DMCError("Invalid write access to register {}".format(hex(address)))

    def output(self):
        return 0