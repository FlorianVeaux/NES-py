import numpy as np
from nes.cpu import CPU
from nes.memory import Memory
import pdb
import os

def _abs_path(path):
    _dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(_dir, path)

def test_cpu():
    """Tests CPU againsts a benchmark."""
    ms6502 = CPU()

    benchmark = open(_abs_path('benchmark.txt'))
    f = open(_abs_path('nestest.nes'), 'rb')
    data = np.zeros(24592, dtype='uint8')
    i = 0
    b = f.read(1)
    while b != b'':
        data[i] = b[0]
        i = i+1
        b = f.read(1)
    ms6502.memory.load_ROM(0xbff0, data)
    ms6502.memory.store(0x0180, 0x33)
    ms6502.memory.store(0x017F, 0x69)
    ms6502.memory.store(0xA9A9, 0xA9)

    ms6502.memory.store(0x4004, 0xFF)
    ms6502.memory.store(0x4005, 0xFF)
    ms6502.memory.store(0x4006, 0xFF)
    ms6502.memory.store(0x4007, 0xFF)
    ms6502.memory.store(0x4015, 0xFF)
    ms6502.pc = 0xC000
    total_cycles = 0
    nb_fails = 0
    while(True):
        debug_data = ms6502.step(debug=True)
        string = debug_data['PC'] + "  "
        string += debug_data['opcode'] + " "
        for arg in debug_data['args']:
            string += arg + " "
        string = string.ljust(15)
        string += debug_data['mneumonic']
        string = string.ljust(48)
        string += debug_data['A'] + " " + debug_data['X'] + " " + debug_data['Y'] + " " + debug_data['P'] + " "
        string += debug_data['SP'] + " "
        cyc_string = str(total_cycles % 341).rjust(3)
        string += "CYC:{}".format(cyc_string)
        total_cycles += 3*int(debug_data['cycles'])

        benchmark_line = benchmark.readline()[:81]
        if(string == benchmark_line):
            print(string)
        else:
            print("CPU:      " + string)
            print("Expected: " + benchmark_line)
            nb_fails += 1
            if nb_fails == -1:
                pdb.set_trace()
                exit(0)
