from enum import IntEnum


# Size of one name table (including its attribute table)
TABLE_SIZE = 0x0400
# Corresponds to the 0 of the name tables
OFFSET = 0x2000


class Mirroring(IntEnum):
    """Controls the mirroring for the PPU nametables."""
    horizontal = 0
    vertical = 1

def mirror_map(mirroring):
    if mirroring == Mirroring.horizontal:
        # Then table 1 = table 0 and table 3 = table 2
        return [0, 0, 2, 2]
    if mirroring == Mirroring.vertical:
        # Then table 3 == table 0 and table 3 == table 1
        return [0, 1, 0, 1]

def mirrored_address(address, mirroring):
    pointer = address - OFFSET
    table_number, r = pointer // TABLE_SIZE, pointer % TABLE_SIZE
    return OFFSET + mirror_map(mirroring)[table_number] * TABLE_SIZE + r

