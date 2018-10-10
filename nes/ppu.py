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
    """OAMDATA contains up to 64 sprites on 4 bytes each.
        - byte 0: Y position
        - byte 1: tile index
        - byte 2: attributes
        - byte 3: X position
    """
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
        self.background_data = 0 # 64 bits!

        # SPRITE TEMP VARS
        sprite_count = 0
        sprite_graphics = [] # 32 bits * 8
        sprite_positions = [] # 1 bytes * 8
        sprite_priorities = [] # 1 byte * 8
        sprite_indexes = [] # 1 byte * 8

    def reset(self):
        self.clock = 340
        self.scan_line = 240
        self.PPUCTRL.write(0)
        self.PPUMASK.write(0)
        self.OAMADDR.write(0)

    def tick(self):
        # TODO: nmi related logic

        # jump on odd frames for the prerender line if render is set
        if self.PPUMASK.sprite_flag or self.PPUMASK.background_flag:
            if not self.is_even_screen and \
                self.scan_line == 261 and \
                self.clock == 339:
                self.clock = 0
                self.scan_line = 0
                self.is_even_screen = not self.is_even_screen
                return

        self.clock += 1
        if self.clock == PPU.CLOCK_CYCLE:
            self.clock = 0
            self.scan_line += 1
            if self.scan_line == PPU.PRE_RENDER_SCAN_LINE:
                self.scan_line = 0
                self.is_even_screen = not self.is_even_screen


    def render_pixel(self):
        x, y = self.clock - 1, self.scan_line
        background = self.get_background_pixel()
        i, sprite = self.get_sprite_pixel()
        if x < 8 and not self.PPUMASK.left_background_flag:
            background = 0
        if x < 8 and not self.PPUMASK.left_sprites_flag:
            sprite = 0
        # Transparency checks
        b, s = background % 4 != 0, sprite % 4 != 0
        if not b and not s:
            color = 0
        elif not b and s:
            color = sprite | 0x10
        elif not s and b:
            color = background
        else:
            if self.sprite_indexes[i] == 0 and x < 255:
                self.PPUSTATUS.sprite_zero_flag = 1
            if self.sprite_priorities[i] == 0:
                color = sprite | 0x10
            else:
                color = background

        palette_info = self.memory.read(0x3F00 + color % 64)
        # TODO: finish this
        # define a palette with all colors
        # c = palette[palette_info]
        # render pixel on scren
        # self._console.screen.setRGB(x, y, c)

    def increment_horizontal_scroll(self):
        """increment hori(v)"""
        if self.v & 0x001F == 31:
            # then set coarse X to 0
            self.v &= 0xFFE0
            # switch horizontal nametable
            self.v ^= 0x0400
        else:
            # increment coarse X
            self.v += 1

    def increment_vertical_scroll(self):
        """increment vert(v)"""
        # if fine Y < 7, increment it
        if self.v & 0x7000 != 0x7000:
            self.v += 0x1000
        else:
            # fine Y = 0
            self.v &= 0x8FFF
            # let y = coarse Y
            y = (self.v & 0x03E0) >> 5
            if y == 29:
                y = 0
                # switch vertical nametable
                ppu.v ^= 0x0800
            elif y == 31:
                y = 0
            else:
                y += 1
            # put coarse Y back into v
            self.v = (self.v & 0xFC1F) | (y << 5)

    def copy_horizontal_scroll(self):
        """hori(v) = hori(t)"""
        self.v = (self.v & 0xFBE0) | (self.t & 0x041F)

    def copy_vertical_scroll(self):
        """vert(v) = vert(t)"""
        self.v = (self.v & 0x841F) | (self.t & 0x7BE0)

    def get_sprite_pixel(self):
        """Returns the sprite pixel that will be considered for rendering, as
        well as the sprite index."""
        if not self.PPUMASK.sprite_flag:
            return 0, 0
        for i in range(self.sprite_count):
            # relative X position compared to beginning of sprite
            offset = (self.clock - 1) - self.sprite_positions[i]
            if offset < 0 or offset > 7:
                continue
            color = (self.sprite_graphics[i] >> (7 - offset) * 4) & 0xF
            if color % 4 == 0:
                # sprite is transparent
                continue
            # Even if other sprites were to be set at this coordinate, we only
            # render the first one anyway.
            return i, color
        return 0, 0

    def fetch_sprite_graphics(i, row):
        """Gets the 8 pixel's worth of graphical data for the given sprite.
        Args:
            row: the row WITHIN the sprite (0 == top of sprite)
        """
        tile_index = self.OAMDATA.data[i * 4 + 1]
        attributes = self.OAMDATA.data[i * 4 + 2]
        vertical_flip = attributes & 0x80 == 0x80
        horizontal_flip = attribute & 0x40 == 0x40
        if not self.PPUCTRL.sprite_size_flag:
            # sprite of size 8
            if vertical_flip:
                row = 7 - row
            table = self.PPUCTRL.sprite_table_flag
        else:
            if vertical_flip:
                row = 15 - row
            # In that case, the lowest byte gives the table number and the
            # highest 7 the tile number
            table = tile_index & 1
            tile_index &= 0xFE
            if row > 7:
                tile_index += 1
                row -= 8
        address = 0x1000 * table + 0x10 * tile + row
        low_tile_byte = self.memory.read(address)
        high_tile_byte = self.memory.read(address + 8)
        # We now combine together the data for 8 pixels, similar to
        # load_background_data
        a = (attributes & 0x3) << 2
        for i in range(8):
            if horizontal_flip:
                a = (high_tile_byte & 1) << 1
                b = (high_tile_byte & 1) << 0
                low_tile_byte >>= 1
                high_tile_byte >>= 1
            else:
                b = (high_tile_byte & 0x80) >> 6
                c = (low_tile_byte & 0x80) >> 7
                low_tile_byte <<= 1
                high_tile_byte <<= 1
            data <<= 4
            data |= (a | b | c)
        return data

    def load_sprite_data(self):
        """Gets all sprite data for the current scan line.
        """
        h = 16 if self.PPUCTRL.sprite_size_flag else 8
        data = self.OAMDATA.data
        count = 0
        for i in range(64):
            # get x, y and attribute data
            y, a, x = data[i * 4], data[i * 4 + 2], data[i * 4 + 3]
            top, bottom = y, y + h
            # top is the smallest, bottom the biggest row number
            if self.scan_line < top or self.scan_line > bottom:
                # this sprite does not appear on this line
                continue
            count += 1
            if count <= 8:
                self.sprite_graphics[count] = self.fetch_sprite_graphics(
                    i, self.scan_line - top
                )
                self.sprite_positions[count] = x
                self.sprite_priorities[count] = (a >> 5) & 1
                self.sprite_indexes[count] = i
        if count > 8:
            # no rendering if we hit more than 8 sprites on this line, but
            # set the overflow flag in that case
            count = 8
            self.PPUSTATUS.sprite_overflow_flag = 1
        self.sprite_count = count

    def get_background_pixel(self):
        """Returns the background pixel that will be considered for rendering.
        For that, select the 32 highest bits of the shift register (data that
        has been fetched during the previous cycle) and get the pixel data
        corresponding to the highest 4 bits, minus the fine X scroll (this is
        due to how load_background_data works, the data for the first pixels is
        stored in the highest bits).
        """
        if not self.PPUMASK.background_flag:
            return 0
        # the 4 bit shift on background_data is done in the main PPU loop
        cycle_data = self.background_data >> 32
        pixel_data = (cycle_data >> (7 - self.x) * 4) & 0xF
        return pixel_data

    def load_background_data(self):
        """Each PPU fetch cycle (8 ticks) needs to get the data corresponding to
        half a tile (as it is the data that will be "consumed" to render 8
        pixels, one per tick). That data will be consumed in the NEXT cycle and
        therefore gets loaded as the lowest bits of background data (the highest
        bits being consumed in the current cycle).
        For one given background pixel, the necessary information is as follows:
        A A B C
        ^ ^ ^ ^
        | | | a bit from the lower tile byte
        | | a bit from the higher tile byte
        what palette to use (a.k.a the attribute table byte)
        """
        data = 0
        a = self.attribute_table_byte
        for i in range(8):
            b = (self.high_tile_byte & 0x80) >> 6
            c = (self.low_tile_byte & 0x80) >> 7
            data <<= 4
            self.high_tile_byte <<= 1
            self.low_tile_byte <<= 1
            data |= (a | b | c)
        self.background_data |= data


    def fetch_name_table_byte(self):
        """The name table address is given by a $2000 offset combined with the
        12 lowest bits of the VRAM address.
        """
        address = self.v & 0xFFF # select 12 bytes
        self.name_table_byte = self.memory.read(0x2000 + address)

    def fetch_attribute_table_byte(self):
        """To get the attribute table byte, we need to combine:
            - the 2 bits selecting the name table,
            - the three highest bits of the coarse Y scroll,
            - the three highest bits of the coarse X scroll
        With a #23C0 offset.
        """
        address = 0x23C0
        address |= self.v & 0xC00
        address |= (self.v & 0x380) >> 4
        address |= (self.v & 0x1C) >> 2
        self.attribute_table_byte = self.memory.read(address)

    def fetch_lower_tile_byte(self):
        """To fetch a tile byte, combine:
            - table index(stored in PPUCTRL) * $1000
            - tile index (in the name table byte) * $10
            - fine Y scroll (3 highest bits of VRAM address)
        """
        fine_y = (self.v >> 12) & 0x7
        table_index = self.PPUCTRL.background_table_flag
        tile_index = self.name_table_byte
        address = 0x1000 * table_index + 0x10 * tile_index + fine_y
        self.low_tile_byte = self.memory.read(address)

    def fetch_higher_tile_byte(self):
        """Read one byte above the lower tile byte
        """
        fine_y = (self.v >> 12) & 0x7
        table_index = self.PPUCTRL.background_table_flag
        tile_index = self.name_table_byte
        address = 0x1000 * table_index + 0x10 * tile_index + fine_y
        self.high_tile_byte = self.memory.read(address + 8)

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
                    self.background_data <<= 4
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

                if self.clock == 257:
                    # In a real NES, this would be performed over several
                    # cycles. Here, we do it at once
                    self.load_sprite_data()

                # TODO: implement 2 last cycle logic?

            if is_prerender_line:
                if self.clock == 1:
                    self.PPUSTATUS.vertical_blank_started_flag = 0
                    self.PPUSTATUS.sprite_overflow_flag = 0
                    self.PPUSTATUS.sprite_zero_flag = 0

                if 280 <= self.clock <= 304:
                    self.copy_vertical_scroll()

                # The jump on odd screens is peformed in tick()

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
