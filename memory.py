# must implement
# reset()
# fetch (address) return value
# storei (address, value) return old_value


import numpy as np


class Memory(object):
    MEM_SIZE = 65536

    def __init__(self):
        self._memory = np.zeros(MEM_SIZE, dtype='uint8')

    def reset(self):
        self._memory = np.zeros(MEM_SIZE, dtype='uint8')
        
    def fetch(self, address):
        return self._memory[address]

    def store(self, address, value):
        tmp = self._memory[address]
        self._memory[address] = value
        return tmp

    @staticmethod
    def create():
        return Memory()
    
