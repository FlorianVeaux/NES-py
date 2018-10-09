class PPUError(Exception):
    """Base error class"""


class PPURegisterError(PPUError):
    """Raise on Register error"""
    def __init__(self, message, register):
        message = '({0}) {1}'.format(register.__class__.__name__, message)
        super().__init__(message)


class Register:
    def read(self):
        raise PPURegisterError('Read is not supported.', self)

    def write(self, value):
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
    # Constants
    CLOCK_CYCLE = 341
    VISIBLE_CLOCK_CYCLE = 256
    PRE_RENDER_SCAN_LINE = 261
    POST_RENDER_SCAN_LINE = 240

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

        # RENDERING
        self.clock = 0
        self.scan_line = 0
        self.is_even_screen = True

        # BACKGROUND TEMP VARS
        self.name_table_byte = 0
        self.attribute_table_byte = 0
        self.lower_tile_byte = 0
        self.higher_tile_byte = 0
        self.loaded_data = 0 # 32 bits!

    def tick(self):
        self.clock += 1
        if self.clock == PPU.CLOCK_CYCLE:
            self.clock = 0
            self.scan_line += 1
            if self.scan_line == PPU.PRE_RENDER_SCAN_LINE:
                self.scan_line = 0
                self.is_even_screen = not self.is_even_screen


    def render_pixel(self):
        raise NotImplementedError

    def increment_horizontal_scroll(self):
        raise NotImplementedError

    def increment_vertical_scroll(self):
        raise NotImplementedError

    def copy_horizontal_scroll(self):
        raise NotImplementedError

    def copy_vertical_scroll(self):
        raise NotImplementedError

    def load_background_data(self):
        raise NotImplementedError

    def fetch_name_table_byte(self):
        raise NotImplementedError

    def fetch_attribute_table_byte(self):
        raise NotImplementedError

    def fetch_lower_tile_byte(self):
        raise NotImplementedError

    def fetch_higher_tile_byte(self):
        raise NotImplementedError

    def step(self):
        self.tick()
        rendering_enabled = self.PPUMASK.background_flag or self.PPUMASK.sprite_flag
        is_visible_clock = 1 <= self.clock <= 256
        is_visible_line = self.scan_line < PPU.POST_RENDER_SCAN_LINE
        is_prerender_line = self.scan_line == PPU.PRE_RENDER_SCAN_LINE
        is_postrender_line = self.scan_line == PPU.POST_RENDER_SCAN_LINE
        is_fetch_line = is_visible_line or is_prerender_line
        is_fetch_clock = is_visible_clock or 321 <= self.clock <= 336

        if rendering_enabled:
            if is_visible_line and is_visible_clock:
                self.render_pixel()

            if is_fetch_line:
                if is_fetch_clock:
                    # LINES: 0 - 239, 261; CLOCK: 1 - 256, 321 - 336
                    switch = self.clock % 8
                    # Make sure that we have 8 new bits every 2 ticks:
                    loaded_data >> 4
                    if switch == 0:
                        self.increment_horizontal_scroll()
                        # load some new data
                        self.load_background_data()
                    if switch == 1:
                        self.fetch_name_table_byte()
                    elif switch == 3:
                        self.fetch_attribute_table_byte()
                    elif switch == 5:
                        self.fetch_lower_tile_byte()
                    elif switch == 7:
                        self.fetch_higher_tile_byte()

                if self.clock == 256:
                    self.increment_vertical_scroll()

                if self.clock == 257:
                    self.copy_horizontal_scroll()

                # TODO: implement sprite logic
                # TODO: implement 2 last cycle logic

            if is_prerender_line:
                if self.clock == 1:
                    self.PPUSTATUS.vertical_blank_started_flag = 0
                    self.PPUSTATUS.sprite_overflow_flag = 0
                    self.PPUSTATUS.sprite_zero_flag = 0

                # TODO: jump or not depending on frame parity

                if 280 <= self.clock <= 304:
                    self.copy_vertical_scroll()

            if is_postrender_line and self.clock == 1:
                self.PPUSTATUS.vertical_blank_started_flag = 1

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

    def write_register(self, address, value):
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
