class PPU:
    def __init__(self): 
        # REGISTERS

        # $2000: PPUCTRL
        nametable_flag = 0          # On two bits! 0:$2000, 1:$2400, 2:$2800, 3:$2C00
        increment_flag = 0          # 0: add 1 (going accross), 1: add 32 (going down)
        sprite_table_flag = 0       # 0: $0000, 1:1000; ignored in 8x16 
        background_table_flag = 0   # 0: $0000, 1: $1000
        sprite_size_flag = 0        # 0: 8x8, 1: 16x16
        master_slave_flag = 0       # 0: read from EXT, 1: write to EXT
        nmi_flag = 0                # 0:off, 1: on

        # $2001: PPUMASK
        greyscale_flag = 0          # 0: normal, 1: greyscale
        left_background_flag = 0    # 0: hide, 1: show
        left_sprites_flag = 0       # 0: hide, 1: show
        background_flag = 0         # 0: hide, 1: show
        sprites_flag = 0            # 0: hide, 1: show
        red_emphasize_flag = 0      # 0: off, 1: on
        green_emphasize_flag = 0    # 0: off, 1: on
        blue_emphasize_flag = 0     # 0: off, 1: on

        # $2002: PPUSTATUS
        sprite_overflow_flag = 0
        sprite_zero_flag = 0
        vertical_blank_started_flag = 0

        # $2003: OAMADDR
        # $2004: OAMDATA
        # $2005: PPUSCROLL
        # $2006: PPUADDR
        # $2007: PPUDATA
