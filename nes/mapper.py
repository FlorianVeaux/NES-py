from nes.utility import parse_nes_file
from nes.cartridge import Cartridge
import logging


log = logging.getLogger('nes.' + __name__)


class Mapper:
    """Base Mapper class. Extend to create a new mapper"""
    def __init__(self, cartridge):
        self._cartridge = cartridge

    def read_prg(self, address):
        raise NotImplementedError

    def write_prg(self, address, value):
        raise NotImplementedError

    def read_chr(address):
        raise NotImplementedError

    def write_chr(self, address, value):
        raise NotImplementedError

    @staticmethod
    def from_nes_file(nesfile):
        """Create a Mapper and associeted Cartridge from a NES file. For more
        info, see utility.py"""
        with open(nesfile, 'rb') as f:
            data = parse_nes_file(f)
        mapper_id = data[0]
        klass = MAPPER_BY_ID[mapper_id] if mapper_id in MAPPER_BY_ID else Mapper
        cartridge = Cartridge(*data[1:])
        return klass(cartridge)


class NROMMapper(Mapper):
    """Generic Nintendo board. Banks are as follows:
        $6000 - $7FFF : PRG RAM
        $8000 - $BFFF : PRG ROM (lower)
        $C000 - $FFFF : PRG ROM (upper) or mirror of lower (NROM-128)
    NROM-128 have a PRG_ROM of 16kB. NROM-256 have a PRG_ROM of 32kB.
    """
    def __init__(self, cartridge):
        super().__init__(cartridge)
        self.is_nrom_128 = cartridge.prg_rom_size == 0x4000

    def read_prg(self, address):
        # Careful, this spams...
        # log.debug('Reading PRG at %s', hex(address))
        if address < 0x8000:
            return self._cartridge.read_prg_ram(address - 0x6000)
        else:
            pointer = address - 0x8000
            if self.is_nrom_128:
                return self._cartridge.read_prg_rom(pointer % 0x4000)
            return self._cartridge.read_prg_rom(pointer)


# Map of supported Mappers. See https://wiki.nesdev.com/w/index.php/Mapper.
MAPPER_BY_ID = {
    0: NROMMapper,
}



