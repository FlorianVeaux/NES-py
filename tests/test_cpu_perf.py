from nes.console import Console
from tests.utils import Profiler, abs_path


def test_cpu_perf():
    console = Console(abs_path('color_test.nes'))
    cpu = console.cpu
    CYCLES = 300000

    sp = Profiler('step.profile')
    with sp as p:
        for i in range(CYCLES):
            cpu.step()

    # rp = Profiler('read.profile')
    # with rp as p:
    #     for i in range(CYCLES):
    #         cpu.memory.read(0xFFFF)
