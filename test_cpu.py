""" Do some sanity tests here. This is more to assert that our code runs without
"dumb" errors than to ensure correctness. For this, rely on ROM tests.
"""
from unittest.mock import patch
from cpu import CPU, AddressingMode


VAL = 0b10101010


def is_byte(val):
    """Assert that val is indeed on 8 bits only"""
    return val & 0xff == val


@patch('cpu.CPU.read_uint8', return_value=VAL)
@patch('cpu.CPU.write_uint8')
def test_asl(mock_write, mock_read):
    """Arithmetic left shift. Behaves differently in Accumulator mode.
    """
    expected = 0b01010100
    # accumulator mode
    cpu = CPU()
    cpu.A = VAL
    cpu._asl(0, AddressingMode.modeAccumulator)
    assert (cpu.C, cpu.N, cpu.Z) == (1, 0, 0)
    assert cpu.A == expected
    assert not mock_write.called
    assert is_byte(cpu.A)
    # usual mode
    cpu = CPU()
    cpu._asl(0, AddressingMode.modeAbsolute)
    assert (cpu.C, cpu.N, cpu.Z) == (1, 0, 0)
    assert cpu.A == 0
    assert mock_write.calledWith(0, expected)
    assert is_byte(mock_write.call_args[0][0])


@patch('cpu.CPU.read_uint8', return_value=VAL)
def test_and(mock):
    cpu = CPU()
    cpu.A = 0b11011011
    cpu._and(0, 0)
    assert cpu.A == 0b10001010
    assert is_byte(cpu.A)
    assert (cpu.N, cpu.Z) == (1, 0)



