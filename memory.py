# must implement
# reset()
# fetch (address) return value
# storei (address, value) return old_value


import numpy as np
import pdb

class Memory(object):
    MEM_SIZE = 65536
    
    def __init__(self):
        self._memory = np.zeros(Memory.MEM_SIZE, dtype='uint8')

    def reset(self):
        self._memory = np.zeros(Memory.MEM_SIZE, dtype='uint8')
        
    def fetch(self, address):
        if 0x800 <= address < 0x2000:
            print("Hello")
            print(address)
            address %= 0x800
        return self._memory[address]

    def store(self, address, value): 
        if 0x800 <= address < 0x2000:
            address %= 0x800
        tmp = self._memory[address]
        self._memory[address] = value
        return tmp
        

    def load_ROM(self, initAddress, values):
        endAddress = min(initAddress+values.size, self.MEM_SIZE)
        self._memory[initAddress:endAddress] = values[0:endAddress - initAddress]

    @staticmethod
    def create():
        return Memory()

    @staticmethod
    def get_stack_address(address):
        return 0x1A0 | address

    
