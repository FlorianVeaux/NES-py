# must implement
# reset()
# fetch (address) return value
# storei (address, value) return old_value


import numpy as np

MEM_SIZE = 65536

class Memory(object):
    def __init__(self):
        self._memory = np.zeros(MEM_SIZE, dtype='uint8')

    def reset():
        pass
        
    
