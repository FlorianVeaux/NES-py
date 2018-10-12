from nes.utility import parse_nes_file
import numpy as np
import logging


log = logging.getLogger('nes.' + __name__)


class Mapper:
    """Base Mapper class. Extend to create a new mapper"""
    def __init__(self, mirror_id, prg_rom, chr_rom=[],
                prg_ram_size=0, chr_ram_size=0):
        self.mirror_id = mirror_id
        self.prg_rom_size = len(prg_rom)
        self.chr_rom_size = len(chr_rom)
        self.prg_ram_size = prg_ram_size
        self.chr_ram_size = chr_ram_size
        self.PRG_ROM = prg_rom
        self.CHR_ROM = chr_rom
        if chr_ram_size:
            self.CHR_RAM = [0 for i in range(chr_ram_size)]
        if prg_ram_size:
            self.CHR_RAM = [0 for i in range(prg_ram_size)]

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
        return klass(mirror_id, *data[1:])


class NROMMapper(Mapper):
    """Generic Nintendo board. Banks are as follows:
        $6000 - $7FFF : PRG RAM
        $8000 - $BFFF : PRG ROM (lower)
        $C000 - $FFFF : PRG ROM (upper) or mirror of lower (NROM-128)
    NROM-128 have a PRG_ROM of 16kB. NROM-256 have a PRG_ROM of 32kB.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.is_nrom_128 = self.prg_rom_size == 0x4000

    def read_prg(self, address):
        # Careful, this spams...
        # log.debug('Reading PRG at %s', hex(address))
        if address < 0x8000:
            return self.PRG_RAM[address - 0x6000]
        else:
            pointer = address - 0x8000
            if self.is_nrom_128:
                return self.PRG_ROM[pointer % 0x4000]
            return self.PRG_ROM[pointer]

    def write_prg(self, address, value):
        if 0x6000 <= address < 0x8000:
            self.PRG_RAM[address - 0x6000] = value
        else:
            raise NotImplementedError("Trying to write prg at {}".format(hex(address)))

    def read_chr(self, address):
        return self.CHR_ROM[address]

    def write_chr(self, address, value):
        self.CHR_ROM[address] = value


# Map of supported Mappers. See https://wiki.nesdev.com/w/index.php/Mapper.
MAPPER_BY_ID = {
    0: NROMMapper,
}



