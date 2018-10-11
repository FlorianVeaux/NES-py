from tests.utils import Profiler
import numpy as np

X = np.uint8(1)
Y = np.int(1)
Z = 1

class A:
    def a_step(self):
        X << 8


class B:
    def b_step(self):
        Y << 8

class C:
    def c_step(self):
        np.uint32(X)



def empty_test_perf():
    CYCLES = 300000
    p = Profiler('empty')
    a = A()
    b = B()
    c = C()

    with p as f:
        for i in range(CYCLES):
            b.b_step()
            a.a_step()
            c.c_step()
