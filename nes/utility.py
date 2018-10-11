import numpy as np
from collections import namedtuple
import logging

log = logging.getLogger('nes.' + __name__)


PRG_ROM_UNIT = 0x4000
CHR_ROM_UNIT = 0x2000
PRG_RAM_UNIT = 0x2000
HEADER_SIZE = 16
# This defines the NES format
CONSTANT = [0x4e, 0x45, 0x53, 0x1a]


INESHeader = namedtuple('INESHEADER', [
    'prg_rom_size', 'chr_rom_size', 'f6', 'f7', 'prg_ram_size', 'f9', 'f10'
])


class NESParserError(Exception):
    """Base error class"""


def parse_nes_file(f):
    """Takes an open file (as read bytes) and parses it according to
    https://wiki.nesdev.com/w/index.php/INES.

    Returns:
        some header metadata,
        the PRG_ROM data,
        the CHR_ROM data,
        the PRG_RAM size,
        the CHR_RAM size
    """
    _next = lambda: f.read(1)[0]

    header = _extract_header(f)
    log.debug(header)
    prg_rom = _extract_chunk(f, header.prg_rom_size * PRG_ROM_UNIT)
    chr_rom = _extract_chunk(f, header.chr_rom_size * CHR_ROM_UNIT)
    # FIXME: This is for debug purposes. Alert if we missed some data
    assert f.read(1) == b''
    prg_ram_size = header.prg_ram_size * PRG_RAM_UNIT
    # TODO: enable the use of CHR RAM
    chr_ram_size = 0
    # Useful header data
    header_data = {
        'mapper_id': _mapper_id(header),
        'mirror_id': _mirror_id(header)
    }
    return header_data, prg_rom, chr_rom, prg_ram_size, chr_ram_size


def _extract_header(f):
    _next = lambda: f.read(1)[0]
    i = 0
    h = np.zeros(HEADER_SIZE, dtype='int')
    for i in range(HEADER_SIZE):
        b = _next()
        h[i] = b
        # Check that this is indeed a NES file
        if i < len(CONSTANT) and b != CONSTANT[i]:
            raise NESParserError('Not a NES file.')

    # A value 0 of prg_ram in fact means 1
    h[8] = h[8] or 1
    # Populate the header (minus the constant)
    return INESHeader(
        h[4], h[5], h[6], h[7], h[8], h[9], h[10]
    )

def _extract_chunk(f, size):
    """Extracts size bytes from the file and returns the data as a
    numpy array.
    """
    log.debug('Extracting chunk of size %s', size)
    _next = lambda: f.read(1)[0]
    data = np.zeros(size, dtype='int')
    for i in range(size):
        data[i] = _next()
    return data

def _mapper_id(header):
    """Returns the mapper number. See
    https://wiki.nesdev.com/w/index.php/Mapper."""
    # TODO: Add support for more than the 255 mappers encoded on flag6
    return header.f6 >> 4

def _mirror_id(header):
    """Determines the mirroring number."""
    # TODO: Add support for more mirroring options.
    return header.f6 & 1
