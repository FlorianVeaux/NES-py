from tests.utils import Profiler
import numpy as np


T = [1]

class A:
    def __init__(self):
        self.d = np.zeros(0x2000, dtype='int')

    def a_step(self):
        return T[0]





def empty_test_perf():
    CYCLES = 300000
    p = Profiler('empty')
    a = A()

    with p as f:
        for i in range(CYCLES):
            a.a_step()
