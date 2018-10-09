import numpy as np
from nes.memory import PPUMemory

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
    def __init__(self, ppu):
        self.ppu = ppu
        self.nametable_flag = 0          # On two bits! 0:$2000, 1:$2400, 2:$2800, 3:$2C00
        self.increment_flag = 0          # 0: add 1 (going accross), 1: add 32 (going down)
        self.sprite_table_flag = 0       # 0: $0000, 1:1000; ignored in 8x16
        self.background_table_flag = 0   # 0: $0000, 1: $1000
        self.sprite_size_flag = 0        # 0: 8x8, 1: 16x16
        self.master_slave_flag = 0       # 0: read from EXT, 1: write to EXT
        self.nmi_flag = 0                # 0:off, 1: on

    """
    No read access
    def read(self):
        val = self.nametable_flag
        val |= self.increment_flag << 2
        val |= self.sprite_table_flag << 3
        val |= self.background_table_flag << 4
        val |= self.sprite_size_flag << 5
        val |= self.master_slave_flag << 6
        val |= self.nmi_flag << 7
        return val
    """

    def write(self, value):
        self.nametable_flag        = value & 0b00000011
        self.increment_flag        = value & 0b00000100
        self.sprite_table_flag     = value & 0b00001000
        self.background_table_flag = value & 0b00010000
        self.sprite_size_flag      = value & 0b00100000
        self.master_slave_flag     = value & 0b01000000
        self.nmi_flag              = value & 0b10000000

        # t: ...BA.. ........ = d: ......BA
        self.ppu.t = (self.ppu.t & 0b111001111111111) | ((value & 0b00000011) << 10)

class PPUMASK(Register):
    def __init__(self, ppu):
        self.ppu = ppu
        self.greyscale_flag = 0          # 0: normal, 1: greyscale
        self.left_background_flag = 0    # 0: hide, 1: show
        self.left_sprites_flag = 0       # 0: hide, 1: show
        self.background_flag = 0         # 0: hide, 1: show
        self.sprites_flag = 0            # 0: hide, 1: show
        self.red_emphasize_flag = 0      # 0: off, 1: on
        self.green_emphasize_flag = 0    # 0: off, 1: on
        self.blue_emphasize_flag = 0     # 0: off, 1: on

    """
    No read access
    def read(self):
        val = self.greyscale_flag
        val |= self.left_background_flag << 1
        val |= self.left_sprites_flag << 2
        val |= self.background_flag << 3
        val |= self.sprites_flag << 4
        val |= self.red_emphasize_flag << 5
        val |= self.green_emphasize_flag << 6
        val |= self.blue_emphasize_flag << 7
        return val
    """

    def write(self, value):
        self.greyscale_flag        = value & 0b00000001
        self.left_background_flag  = value & 0b00000010
        self.left_sprites_flag     = value & 0b00000100
        self.background_flag       = value & 0b00001000
        self.sprites_flag          = value & 0b00010000
        self.red_emphasize_flag    = value & 0b00100000
        self.green_emphasize_flag  = value & 0b01000000
        self.blue_emphasize_flag   = value & 0b10000000

class PPUSTATUS(Register):
    def __init__(self, ppu):
        self.ppu = ppu
        self.sprite_overflow_flag = 0
        self.sprite_zero_flag = 0
        self.vertical_blank_started_flag = 0

    def read(self):
        val = self.vertical_blank_started_flag << 7
        val |= self.sprite_zero_flag << 6
        val |= self.sprite_overflow_flag << 5

        val |= self.ppu.latch_value & 0x00011111

        # Should start an NMI interrupt
        self.vertical_blank_started_flag = False
        self.ppu.w = False
        return val

    """
    No write access
    def write(self, value):
        self.sprite_overflow_flag        = value & 0b10000000 
        self.sprite_zero_flag            = value & 0b01000000
        self.vertical_blank_started_flag = value & 0b00100000
    """

class OAMADDR(Register):
    def __init__(self, ppu):
        self.ppu = ppu
        self.address = 0x00 # 8 bits

    def write(self, value):
        self.address = value

    def increment(self):
        self.address = (self.address + 1) & 0xFF


class OAMDATA(Register):
    def __init__(self, ppu):
        self.ppu = ppu
        self.data = np.zeros(256, dtype='uint8')

    def read(self):
        oam_address = self.ppu.OAMADDR.address
        return self.data[oam_address]

    def write(self, value):
        oam_address = self.ppu.OAMADDR.address
        self.data[oam_address] = value
        self.ppu.OAMADDR.increment()

    def upload_from_cpu(self, data):
        self.data = data


class PPUSCROLL(Register):
    def __init__(self, ppu):
        self.ppu = ppu

    def write(self, value):
        if self.ppu.w == False:
            # t: ....... ...HGFED = d: HGFED...
            # x:              CBA = d: .....CBA
            # w:                  = 1
            self.ppu.t = (self.ppu.t & 0b111111111100000) | (value>>3)
            self.ppu.x = (value & 0b00000111)
            self.ppu.w = True
        else:
            # t: CBA..HG FED..... = d: HGFEDCBA
            # w:                  = 0
            self.ppu.t = (self.ppu.t & 0b000110000011111) | ((value & 0b111) << 12) | ((value & 0b11111000) << 2)
            self.ppu.w = False

class PPUADDR(Register):
    def __init__(self, ppu):
        self.ppu = ppu

    def write(self, value):
        if self.ppu.w == False:
            # t: .FEDCBA ........ = d: ..FEDCBA
            # t: X...... ........ = 0
            # w:                  = 1
            self.ppu.t = (self.ppu.t & 0b000000011111111) | ((value & 0b00111111) << 8)
            self.ppu.w = True
        else:
            # t: ....... HGFEDCBA = d: HGFEDCBA
            # v                   = t
            # w:                  = 0
            self.ppu.t = (self.ppu.t & 0b111111100000000) | value
            self.ppu.w = False


class PPUDATA(Register):
    def __init__(self, ppu):
        self.ppu = ppu
        self.buffered_data = 0 # Next value to return

    def write(self, value):
        self.ppu.memory.write(self.ppu.v&0x3fff, value)
        if self.ppu.PPUCTRL.increment_flag == 0:
            self.ppu.v += 1
        else:
            self.ppu.v += 32

    def read(self):
        value = self.buffered_data
        self.buffered_data = self.ppu.memory.read(self.ppu.v & 0x3FF)

        if self.ppu.v & 0x3F00 == 0x3F00: # This is a palette, return directly
            value = self.buffered_data

        if self.ppu.PPUCTRL.increment_flag == 0:
            self.ppu.v += 1
        else:
            self.ppu.v += 32
        return value

class OAMDMA(Register):
    def __init__(self, ppu):
        self.ppu = ppu

    def write(self, value):
        begin = value << 8
        end = begin | 0x00FF
        cpu_data = self.ppu.cpu.memory.read_slice(begin, end)
        self.ppu.OAMDATA.upload_from_cpu(cpu_data)

        if self.ppu.clock % 2 == 1:
            self.ppu.cpu.wait_cycles += 514
        else:
            self.ppu.cpu.wait_cycles += 513



class PPU:
    # Constants
    CLOCK_CYCLE = 341
    VISIBLE_CLOCK_CYCLE = 256
    PRE_RENDER_SCAN_LINE = 261
    POST_RENDER_SCAN_LINE = 240

    def __init__(self, console):
        self.memory = PPUMemory(console)
        self.cpu = console.cpu

        # REGISTERS
        # $2000: PPUCTRL
        self.PPUCTRL = PPUCTRL(self)
        # $2001: PPUMASK
        self.PPUMASK = PPUMASK(self)
        # $2002: PPUSTATUS
        self.PPUSTATUS = PPUSTATUS(self)
        # $2003: OAMADDR
        self.OAMADDR = OAMADDR(self)
        # $2004: OAMDATA
        self.OAMDATA = OAMDATA(self)
        # $2005: PPUSCROLL
        self.PPUSCROLL = PPUSCROLL(self)
        # $2006: PPUADDR
        self.PPUADDR = PPUADDR(self)
        # $2007: PPUDATA
        self.PPUDATA = PPUDATA(self)

        self.v = 0x00  # Current VRAM, 15bits
        self.t = 0x00  # Temporary VRAM, 15bits
        self.x = 0b000 # Fine scroll, 3bits
        self.w = False # Write toggle

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

        self.latch_value = value
        if address == 0x2000:
            self.PPUCTRL.write(value)
        elif address == 0x2001:
            self.PPUMASK.write(value)
        elif address == 0x2002:
            self.PPUSTATUS.write(value)
        elif address == 0x2003:
            self.OAMADDR.write(value)
        elif address == 0x2004:
            """if self.isRendering:
                pass"""
            self.OAMDATA.write(value)
        elif address == 0x2005:
            self.PPUSCROLL.write(value)
        elif address == 0x2006:
            self.PPUADDR.write(value)
        elif address == 0x2007:
            self.PPUDATA.write(value)
        else:
            raise PPUError('Unknown register of address={}'.format(address))
