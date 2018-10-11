from nes.console import Console
import os
import time
import cProfile

def _abs_path(path):
    _dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(_dir, path)

def test_ppu():
    console = Console(_abs_path('color_test.nes'))
    t = time.time()
    # pr = cProfile.Profile()
    # pr.enable()
    total_cycles = 0
    while True:
        console.step(debug=True)
        frame_num = console.ppu.frame
        if time.time() - t > 10:
            # pr.disable()
            # path = _abs_path('stats')
            # print(path)
            # pr.dump_stats(path)
            # print(frame_num)
            assert False
