import os
import cProfile
from nes.console import Console

def _abs_path(path):
    _dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(_dir, path)

def test_perf():
    console = Console(_abs_path('color_test.nes'))
    CYCLES = 300000
    pr = cProfile.Profile()
    pr.enable()
    for i in range(CYCLES):
        console.step()
    pr.disable()
    pr.dump_stats(_abs_path('perf.profile'))
