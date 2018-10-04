import numpy as np

from memory import Memory

def test_fetch():
    mem = Memory.create()
    mem.store(42, np.uint8(42))
    assert 42 == mem.fetch(42)

def test_reset():
    blank = np.zeros(Memory.MEM_SIZE, dtype='uint8')
    mem = Memory.create()
    mem.store(42, np.uint8(42))
    mem.reset()
    assert all(mem._memory == blank)
    assert mem._memory.dtype == 'uint8'
    
