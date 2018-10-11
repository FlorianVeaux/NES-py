from nes.console import Console
from tests.utils import Profiler, abs_path


def test_cpu_perf():
    console = Console(abs_path('color_test.nes'))
    cpu = console.cpu
    CYCLES = 300000

    sp = Profiler('step')
    with sp as p:
        for i in range(CYCLES):
            cpu.step()

    # rp = Profiler('read8')
    # with rp as p:
    #     for i in range(CYCLES):
    #         cpu.read_uint8(0x1000)

    # rp = Profiler('read16')
    # with rp as p:
    #     for i in range(CYCLES):
    #         cpu.read_uint16(0x1000)
