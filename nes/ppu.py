class PPUError(Exception):
    """Base error class"""


class PPURegisterError(Exception):
    """Raise on Register error"""
    def __init__(self, message, register):
        message = '({0}) {1}'.format(register.__class__.__name__, message)
        super().__init__(message)


class Register:
    def read(self):
        raise PPURegisterError('Read is not supported.', self)

    def write(self, address, value):
        raise PPURegisterError('Write is not supported.', self)


class PPUCTRL(Register):
    def __init__(self):
        nametable_flag = 0          # On two bits! 0:$2000, 1:$2400, 2:$2800, 3:$2C00
        increment_flag = 0          # 0: add 1 (going accross), 1: add 32 (going down)
        sprite_table_flag = 0       # 0: $0000, 1:1000; ignored in 8x16
        background_table_flag = 0   # 0: $0000, 1: $1000
        sprite_size_flag = 0        # 0: 8x8, 1: 16x16
        master_slave_flag = 0       # 0: read from EXT, 1: write to EXT
        nmi_flag = 0                # 0:off, 1: on


class PPUMASK(Register):
    def __init__(self):
        greyscale_flag = 0          # 0: normal, 1: greyscale
        left_background_flag = 0    # 0: hide, 1: show
        left_sprites_flag = 0       # 0: hide, 1: show
        background_flag = 0         # 0: hide, 1: show
        sprites_flag = 0            # 0: hide, 1: show
        red_emphasize_flag = 0      # 0: off, 1: on
        green_emphasize_flag = 0    # 0: off, 1: on
        blue_emphasize_flag = 0     # 0: off, 1: on


class PPUSTATUS(Register):
    def __init__(self):
        sprite_overflow_flag = 0
        sprite_zero_flag = 0
        vertical_blank_started_flag = 0


class OAMADDR(Register):
    pass


class OAMDATA(Register):
    pass


class PPUSCROLL(Register):
    pass


class PPUADDR(Register):
    pass


class PPUDATA(Register):
    pass


class PPU:
    def __init__(self, console):
        # REGISTERS
        # $2000: PPUCTRL
        self.PPUCTRL = PPUCTRL()
        # $2001: PPUMASK
        self.PPUMASK = PPUMASK()
        # $2002: PPUSTATUS
        self.PPUSTATUS = PPUSTATUS()
        # $2003: OAMADDR
        self.OAMADDR = OAMADDR()
        # $2004: OAMDATA
        self.OAMDATA = OAMDATA()
        # $2005: PPUSCROLL
        self.PPUSCROLL = PPUSCROLL()
        # $2006: PPUADDR
        self.PPUADDR = PPUADDR()
        # $2007: PPUDATA
        self.PPUDATA = PPUDATA()


    def read_register(self, address):
        """CPU and PPU communicate through the PPU's registers.
        """
        if address == 0x2000:
            self.PPUCTRL.read()
        elif address == 0x2001:
            self.PPUMASK.read()
        elif address == 0x2002:
            self.PPUSTATUS.read()
        elif address == 0x2003:
            self.OAMADDR.read()
        elif address == 0x2004:
            self.OAMDATA.read()
        elif address == 0x2005:
            self.PPUSCROLL.read()
        elif address == 0x2006:
            self.PPUADDR.read()
        elif address == 0x2007:
            self.PPUDATA.read()
        else:
            raise PPUError('Unknown register of address={}'.format(address))

    def write_to_register(self, address, value):
        """CPU and PPU communicate through the PPU's registers.
        """
        if address == 0x2000:
            self.PPUCTRL.write(value)
        elif address == 0x2001:
            self.PPUMASK.write(value)
        elif address == 0x2002:
            self.PPUSTATUS.write(value)
        elif address == 0x2003:
            self.OAMADDR.write(value)
        elif address == 0x2004:
            self.OAMDATA.write(value)
        elif address == 0x2005:
            self.PPUSCROLL.write(value)
        elif address == 0x2006:
            self.PPUADDR.write(value)
        elif address == 0x2007:
            self.PPUDATA.write(value)
        else:
            raise PPUError('Unknown register of address={}'.format(address))
