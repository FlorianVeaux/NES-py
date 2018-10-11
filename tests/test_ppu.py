from nes.console import Console
import os
import time
import cProfile

def _abs_path(path):
    _dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(_dir, path)

def test_ppu():
    console = Console(_abs_path('color_test.nes'), debug=True)
    t = time.time()
    total_cycles = 0
    while True:
        console.step()
        frame_num = console.ppu.frame
        if time.time() - t > 10:
            console.debugger.dump(_abs_path('cpu_ops.txt'))
            assert False
