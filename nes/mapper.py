from nes.utility import parse_nes_file
from nes.cartridge import Cartridge
import logging


log = logging.getLogger('nes.' + __name__)


class Mapper:
    """Base Mapper class. Extend to create a new mapper"""
    def __init__(self, cartridge, mirror_id):
        self._cartridge = cartridge
        self.mirror_id = mirror_id

    def read_prg(self, address):
        raise NotImplementedError

    def write_prg(self, address, value):
        raise NotImplementedError

    def read_chr(self, address):
        raise NotImplementedError

    def write_chr(self, address, value):
        raise NotImplementedError

    @staticmethod
    def from_nes_file(nesfile):
        """Create a Mapper and associeted Cartridge from a NES file. For more
        info, see utility.py"""
        with open(nesfile, 'rb') as f:
            data = parse_nes_file(f)
        metadata = data[0]
        mapper_id, mirror_id = metadata['mapper_id'], metadata['mirror_id']
        klass = MAPPER_BY_ID[mapper_id] if mapper_id in MAPPER_BY_ID else Mapper
        cartridge = Cartridge(*data[1:])
        return klass(cartridge, mirror_id)


class NROMMapper(Mapper):
    """Generic Nintendo board. Banks are as follows:
        $6000 - $7FFF : PRG RAM
        $8000 - $BFFF : PRG ROM (lower)
        $C000 - $FFFF : PRG ROM (upper) or mirror of lower (NROM-128)
    NROM-128 have a PRG_ROM of 16kB. NROM-256 have a PRG_ROM of 32kB.
    """
    def __init__(self, cartridge, mirror_id):
        super().__init__(cartridge, mirror_id)
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

    def write_prg(self, address, value):
        if 0x6000 <= address < 0x8000:
            self._cartridge.write_prg_ram(address - 0x6000)
        else:
            raise NotImplementedError("Trying to write prg at {}".format(hex(address)))

    def read_chr(self, address):
        return self._cartridge.read_chr_rom(address)

    def write_chr(self, address, value):
        return self._cartridge.write_chr_rom(address, value)


# Map of supported Mappers. See https://wiki.nesdev.com/w/index.php/Mapper.
MAPPER_BY_ID = {
    0: NROMMapper,
}



