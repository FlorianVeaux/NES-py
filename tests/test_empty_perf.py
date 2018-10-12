from tests.utils import Profiler
import numpy as np


T = [1,2,3]

class A:
    def __init__(self):
        self.d = np.zeros(0x2000, dtype='int')

    def a_step(self):
        address = 0x8000
        return T[0x8000 % 0x3]





def test_empty_perf():
    CYCLES = 700000
    p = Profiler('empty.profile')
    a = A()

    with p as f:
        for i in range(CYCLES):
            a.a_step()
