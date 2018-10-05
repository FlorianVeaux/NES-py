from enum import IntEnum
from memory import Memory

class InterruptType(IntEnum):
    interruptNone = 1
    interruptNMI = 2
    interruptIRQ = 3

class AddressingMode(IntEnum):
    modeAbsolute = 1
    modeAbsoluteX = 2
    modeAbsoluteY = 3
    modeAccumulator = 4
    modeImmediate = 5
    modeImplied = 6
    modeIndexedIndirect = 7
    modeIndirect = 8
    modeIndirectIndexed = 9
    modeRelative = 10
    modeZeroPage = 11
    modeZeroPageX = 12
    modeZeroPageY = 13

# Addressing mode for each instruction
INSTRUCTION_MODES = [
	6, 7, 6, 7, 11, 11, 11, 11, 6, 5, 4, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 12, 12, 6, 3, 6, 3, 2, 2, 2, 2,
	1, 7, 6, 7, 11, 11, 11, 11, 6, 5, 4, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 12, 12, 6, 3, 6, 3, 2, 2, 2, 2,
	6, 7, 6, 7, 11, 11, 11, 11, 6, 5, 4, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 12, 12, 6, 3, 6, 3, 2, 2, 2, 2,
	6, 7, 6, 7, 11, 11, 11, 11, 6, 5, 4, 5, 8, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 12, 12, 6, 3, 6, 3, 2, 2, 2, 2,
	5, 7, 5, 7, 11, 11, 11, 11, 6, 5, 6, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 13, 13, 6, 3, 6, 3, 2, 2, 3, 3,
	5, 7, 5, 7, 11, 11, 11, 11, 6, 5, 6, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 13, 13, 6, 3, 6, 3, 2, 2, 3, 3,
	5, 7, 5, 7, 11, 11, 11, 11, 6, 5, 6, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 12, 12, 6, 3, 6, 3, 2, 2, 2, 2,
	5, 7, 5, 7, 11, 11, 11, 11, 6, 5, 6, 5, 1, 1, 1, 1,
	10, 9, 6, 9, 12, 12, 12, 12, 6, 3, 6, 3, 2, 2, 2, 2,
]

# Size of each instruction in bytes
INSTRUCTION_SIZES = [
	1, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
	3, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
	1, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
	1, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 0, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 0, 3, 0, 0,
	2, 2, 2, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
	2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
]

# Number of cycles used by each instruction
INSTRUCTION_CYCLES = [
    7, 6, 2, 8, 3, 3, 5, 5, 3, 2, 2, 2, 4, 4, 6, 6,
	2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
	6, 6, 2, 8, 3, 3, 5, 5, 4, 2, 2, 2, 4, 4, 6, 6,
	2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
	6, 6, 2, 8, 3, 3, 5, 5, 3, 2, 2, 2, 3, 4, 6, 6,
	2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
	6, 6, 2, 8, 3, 3, 5, 5, 4, 2, 2, 2, 5, 4, 6, 6,
	2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
	2, 6, 2, 6, 3, 3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4,
	2, 6, 2, 6, 4, 4, 4, 4, 2, 5, 2, 5, 5, 5, 5, 5,
	2, 6, 2, 6, 3, 3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4,
	2, 5, 2, 5, 4, 4, 4, 4, 2, 4, 2, 4, 4, 4, 4, 4,
	2, 6, 2, 8, 3, 3, 5, 5, 2, 2, 2, 2, 4, 4, 6, 6,
	2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
	2, 6, 2, 8, 3, 3, 5, 5, 2, 2, 2, 2, 4, 4, 6, 6,
	2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
]

INSTRUCTION_PAGE_CYCLES = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0,
]

INSTRUCTION_NAMES = [
	"BRK", "ORA", "KIL", "SLO", "NOP", "ORA", "ASL", "SLO",
	"PHP", "ORA", "ASL", "ANC", "NOP", "ORA", "ASL", "SLO",
	"BPL", "ORA", "KIL", "SLO", "NOP", "ORA", "ASL", "SLO",
	"CLC", "ORA", "NOP", "SLO", "NOP", "ORA", "ASL", "SLO",
	"JSR", "AND", "KIL", "RLA", "BIT", "AND", "ROL", "RLA",
	"PLP", "AND", "ROL", "ANC", "BIT", "AND", "ROL", "RLA",
	"BMI", "AND", "KIL", "RLA", "NOP", "AND", "ROL", "RLA",
	"SEC", "AND", "NOP", "RLA", "NOP", "AND", "ROL", "RLA",
	"RTI", "EOR", "KIL", "SRE", "NOP", "EOR", "LSR", "SRE",
	"PHA", "EOR", "LSR", "ALR", "JMP", "EOR", "LSR", "SRE",
	"BVC", "EOR", "KIL", "SRE", "NOP", "EOR", "LSR", "SRE",
	"CLI", "EOR", "NOP", "SRE", "NOP", "EOR", "LSR", "SRE",
	"RTS", "ADC", "KIL", "RRA", "NOP", "ADC", "ROR", "RRA",
	"PLA", "ADC", "ROR", "ARR", "JMP", "ADC", "ROR", "RRA",
	"BVS", "ADC", "KIL", "RRA", "NOP", "ADC", "ROR", "RRA",
	"SEI", "ADC", "NOP", "RRA", "NOP", "ADC", "ROR", "RRA",
	"NOP", "STA", "NOP", "SAX", "STY", "STA", "STX", "SAX",
	"DEY", "NOP", "TXA", "XAA", "STY", "STA", "STX", "SAX",
	"BCC", "STA", "KIL", "AHX", "STY", "STA", "STX", "SAX",
	"TYA", "STA", "TXS", "TAS", "SHY", "STA", "SHX", "AHX",
	"LDY", "LDA", "LDX", "LAX", "LDY", "LDA", "LDX", "LAX",
	"TAY", "LDA", "TAX", "LAX", "LDY", "LDA", "LDX", "LAX",
	"BCS", "LDA", "KIL", "LAX", "LDY", "LDA", "LDX", "LAX",
	"CLV", "LDA", "TSX", "LAS", "LDY", "LDA", "LDX", "LAX",
	"CPY", "CMP", "NOP", "DCP", "CPY", "CMP", "DEC", "DCP",
	"INY", "CMP", "DEX", "AXS", "CPY", "CMP", "DEC", "DCP",
	"BNE", "CMP", "KIL", "DCP", "NOP", "CMP", "DEC", "DCP",
	"CLD", "CMP", "NOP", "DCP", "NOP", "CMP", "DEC", "DCP",
	"CPX", "SBC", "NOP", "ISC", "CPX", "SBC", "INC", "ISC",
	"INX", "SBC", "NOP", "SBC", "CPX", "SBC", "INC", "ISC",
	"BEQ", "SBC", "KIL", "ISC", "NOP", "SBC", "INC", "ISC",
	"SED", "SBC", "NOP", "ISC", "NOP", "SBC", "INC", "ISC",
]

class CPU:

    def __init__(self):
        self.memory = Memory.create()
        self.total_cycles = 0
        self.step_cycles = 0
        self.pc = 0 # Program counter
        self.sp = 0 # Stack Pointer
        self.A = 0  # Accumulator
        self.X = 0  # Index Register X
        self.Y = 0  # Index Register Y
        # PROCESSOR FLAGS
        self.C = False  # Carry Flag
        self.Z = False  # Zero Flag
        self.I = False  # Interrupt Disable
        self.D = False  # Decimal Mode
        self.B = False  # Break command
        self.O = False  # Overflow flag
        self.N = False  # Negative flag
        #ENDOF PROCESSOR FLAGS
        self.instruction_table = [getattr(self, i) for i in INSTRUCTION_NAMES]
    
    def read_uint8(self, address):
        """Reads a byte from the memory at the given address
        """

        return self.memory.fetch(address)

    def read_uint16(self, address):
        """Reads an uint16 from the memory
        """

        lo = self.memory.fetch(address)
        hi = self.memory.fetch(address + 1)
        return hi << 8 | lo

    def push_uint8(self, val):
        """Push the given val onto the stack
        """

        stack_ad = self.memory.get_stack_address(self.sp)
        self.memory.store(stack_ad, val)
        self.sp = self.sp - 1

    def push_uint16(self, val):
        """Push a given uint16 onto the stack
        """
        hi = val >> 8
        lo = val & 0xFF
        self.push_uint8(hi)
        self.push_uint8(lo)

    def pop_uint8(self):
        self.sp = self.sp + 1
        stack_ad = self.memory.get_stack_address(self.sp)
        return self.memory.fetch(stack_ad)

    def pop_uint16(self):
        """Pops two bytes as one number from the stack"""
        lo = self.pop_uint8()
        hi = self.pop_uint8()
        return hi << 8 | lo

    def getFlags(self):
        flags = 0x00
        flags |= self.C << 0
        flags |= self.Z << 1
        flags |= self.I << 2
        flags |= self.D << 3
        flags |= 1 # Not allowed, bug ?
        flags |= self.O << 6
        flags |= self.N << 7
        return flags

    def setFlags(self, flags):
        self.C = (flags >> 0) & 1
        self.Z = (flags >> 1) & 1
        self.I = (flags >> 2) & 1
        self.D = (flags >> 3) & 1
        # self.B = (flags >> 4) & 1 Not allowed, bug ?
        self.O = (flags >> 6) & 1
        self.N = (flags >> 7) & 1

    def reset(self):
        self.pc = self.read_uint16(0xFFFC)
        self.sp = 0xFD
        self.setFlags(0b100100)

    def step(self):
        opcode = self.read_uint8(self.pc)
        mode = INSTRUCTION_MODES[opcode]
        page_crossed = False # Set to true when an underlying addition between a uint16 and a uint8 carries to the high byte
        self.step_cycles = 0
        
        if mode == AddressingMode.modeAbsolute:
            arg = self.read_uint16(self.pc + 1)
        elif mode == AddressingMode.modeAbsoluteX:
            uint16_address = self.read_uint16(self.pc + 1)
            uint8_index_register = self.X

            arg = uint16_address + uint8_index_register
            page_crossed = self.pagesDiffer(uint16_address, arg)
        elif mode == AddressingMode.modeAbsoluteY:
            uint16_address = self.read_uint16(self.pc + 1)
            uint8_index_register = self.Y

            arg = uint16_address + uint8_index_register
            page_crossed = self.pagesDiffer(uint16_address, arg)
        elif mode == AddressingMode.modeAccumulator:
            # Works on self.A directly
            arg = 0
        elif mode == AddressingMode.modeImmediate:
            arg = self.pc+1
        elif mode == AddressingMode.modeImplied:
            # For many 6502 instructions the source and destination of the information to be
            # manipulated is implied directly by the function of the instruction itself and
            # no further operand needs to be specified. Operations like 'Clear Carry Flag'
            # (CLC) and 'Return from Subroutine' (RTS) are implicit.
            arg = 0
        elif mode == AddressingMode.modeIndexedIndirect:
            # Warning, there's a bug, the addition with X does not carry. TODO Need to be implemented
            arg = self.read_uint16(self.read_uint16(self.pc + 1) + self.X)
        elif mode == AddressingMode.modeIndirect:
            # Same bug
            arg = self.read_uint16(self.read_uint16(self.pc + 1))
        elif mode == AddressingMode.modeIndirectIndexed:
            # Same bug
            arg = self.read_uint16(self.read_uint16(self.pc + 1)) + self.Y
            page_crossed = self.pagesDiffer(arg - self.Y, arg)
        elif mode == AddressingMode.modeRelative:
            branch_offset = self.read_uint8(self.pc + 1)
            if(branch_offset & 0b10000000):
                branch_offset = branch_offset - 256

            arg = self.pc + 1 + branch_offset
        elif mode == AddressingMode.modeZeroPage:
            arg = self.read_uint8(self.pc + 1)
        elif mode == AddressingMode.modeZeroPageX:
            # Wraps around to stay on Zero page
            arg = (self.read_uint8(self.pc + 1) + self.X) & 0xff
        elif mode == AddressingMode.modeZeroPageY:
            # Wraps around to stay on Zero page
            arg = (self.read_uint8(self.pc + 1) + self.Y) & 0xff
        else:
            raise Exception("Unknown mode (%d)" % mode)

        # Increment program counter
        self.pc += INSTRUCTION_SIZES[opcode]
        self.step_cycles += INSTRUCTION_CYCLES[opcode]

        if page_crossed:
            self.step_cycles += INSTRUCTION_PAGE_CYCLES[opcode]
        
        self.execute_instruction(opcode, arg, mode)
        
    def execute_instruction(self, opcode, address, mode):
        self.instruction_table[opcode](address, mode)
    
    @staticmethod
    def pagesDiffer(a1, a2):
        return 0xFF00 & a1 != 0xFF00 & a2

    def set_N(self, val):
        # sets negative flag if val negative (bit 7 set)
        self.N = 1 if val & 0x80 else 0

    def set_Z(self, val):
        # sets zero flag if val is 0
        self.Z = 1 if val == 0 else 0

    def set_ZN(self, val):
        self.set_Z(val)
        self.set_N(val)

    def ADC(self, address, mode):
        a = self.A
        b = self.read_uint8(address)
        c = self.C
        self.A = (a + b + c) & 0xFF
        self.set_ZN(self.A)
        self.C =  a + b + c > 255 # set carry if overflow happens
        self.O = (a^b) & 0b10000000 != 0 and (a^self.A) & 0b10000000 != 0

    def AND(self, address, mode):
        self.A = self.A & self.read_uint8(address)
        self.set_ZN(self.A)

    def ASL(self, address, mode):
        if mode == AddressingMode.modeAccumulator:
            self.C = (self.A >> 7) & 1
            self.A = (self.A << 1) & 0xFF # force register to stay on 8 bits
            self.set_ZN(self.A)
        else:
            value = self.read_uint8(address)
            self.C = (value >> 7) & 1
            value = (value << 1) & 0xFF
            self.set_ZN(value)
            self.memory.store(address, value)

    def BCC(self, address, mode):
        if(not self.C):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BCS(self, address, mode):
        if(self.C):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BEQ(self, address, mode):
        if(self.Z):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BIT(self, address, mode):
        value = self.read_uint8(address)
        self.set_Z(self.A & value)
        self.N = value & 0b10000000
        self.O = value & 0b01000000

    def BMI(self, address, mode):
        if(self.N):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BNE(self, address, mode):
        if(not self.Z):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BPL(self, address, mode):
        if(not self.N):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BRK(self, address, mode):
        self.B = 1
        self.push_uint16(self.pc)
        self.push_uint8(self.getFlags())
        self.pc = self.read_uint16(0xFFFE)

    def BVC(self, address, mode):
        if(not self.O):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed

    def BVS(self, address, mode):
        if(self.O):
            page_crossed = self.pagesDiffer(self.pc, address)
            self.pc = address
            self.step_cycles += 1 + 2*page_crossed


    def CLC(self, address, mode):
        self.C = False

    def CLD(self, address, mode):
        self.D = False

    def CLI(self, address, mode):
        self.I = False

    def CLV(self, address, mode):
        self.O = False

    def CMP(self, address, mode):
        mem_val = self.read_uint8(address)
        self.C = self.A >= mem_val
        self.set_ZN(self.A - mem_val)

    def CPX(self, address, mode):
        mem_val = self.read_uint8(address)
        self.C = self.X >= mem_val
        self.set_ZN(self.X - mem_val)

    def CPY(self, address, mode):
        mem_val = self.read_uint8(address)
        self.C = self.Y >= mem_val
        self.set_ZN(self.Y - mem_val)

    def DEC(self, address, mode):
        new_val = (self.read_uint8(address) - 1) & 0xFF
        self.memory.store(address, new_val)
        self.set_ZN(new_val)

    def DEX(self, address, mode):
        self.X = (self.X - 1) & 0xFF
        self.set_ZN(self.X)

    def DEY(self, address, mode):
        self.Y = (self.Y - 1) & 0xFF
        self.set_ZN(self.Y)

    def EOR(self, address, mode):
        self.A = self.A ^ self.read_uint8(address)
        self.set_ZN(self.A)

    def INC(self, address, mode):
        new_val = (self.read_uint8(address) + 1) & 0xFF
        self.memory.store(address, new_val)
        self.set_ZN(new_val)

    def INX(self, address, mode):
        self.X = (self.X + 1) & 0xFF
        self.set_ZN(self.X)

    def INY(self, address, mode):
        self.Y = (self.Y + 1) & 0xFF
        self.set_ZN(self.Y)

    def JMP(self, address, mode):
        self.pc = address

    def JSR(self, address, mode):
        self.push_uint16(self.pc - 1)
        self.pc = address

    def LDA(self, address, mode):
        self.A = self.read_uint8(address)
        self.set_ZN(self.A)

    def LDX(self, address, mode):
        self.X = self.read_uint8(address)
        self.set_ZN(self.X)

    def LDY(self, address, mode):
        self.Y = self.read_uint8(address)
        self.set_ZN(self.Y)

    def LSR(self, address, mode):
        if mode == AddressingMode.modeAccumulator:
            self.C = self.A & 1
            self.A >> 1
            self.set_ZN(self.A)
        else:
            value = self.read_uint8(address)
            self.C = value & 1
            value >> 1
            self.memory.store(address, value)
            self.set_ZN(value)

    def NOP(self, address, mode):
        pass

    def ORA(self, address, mode):
        self.A |= self.read_uint8(address)
        self.set_ZN(self.A)

    def PHA(self, address, mode):
        self.memory.store(address, self.A)

    def PHP(self, address, mode):
        self.memory.store(address, self.getFlags())

    def PLA(self, address, mode):
        self.A = self.pop_uint8()
        self.set_ZN(self.A)

    def PLP(self, address, mode):
        self.setFlags(self.pop_uint8())

    def ROL(self, address, mode):
        if mode == AddressingMode.modeAccumulator:
            hi_a = self.A & 0b10000000
            self.A = (self.A << 1) | (self.C)
            self.C = hi_a
            self.set_ZN(self.A)
        else:
            value = self.read_uint8(address)
            hi_a = value & 0b10000000
            value = (value << 1) | (self.C)
            self.C = hi_a
            self.memory.store(address, value)
            self.set_ZN(value)

    def ROR(self, address, mode):
        if mode == AddressingMode.modeAccumulator:
            lo_a = self.A & 1
            self.A = (self.A >> 1) | (self.C << 7)
            self.C = lo_a
            self.set_ZN(self.A)
        else:
            value = self.read_uint8(address)
            lo_a = value & 1
            value = (value >> 1) | (self.C << 7)
            self.C = lo_a
            self.memory.store(address, value)
            self.set_ZN(value)

    def RTI(self, address, mode):
        self.setFlags(self.pop_uint8())
        self.pc = self.pop_uint16()

    def RTS(self, address, mode):
        self.pc = self.pop_uint16() + 1

    def SBC(self, address, mode):
        a = self.A
        b = self.read_uint8(address)
        result = a - b - (1 - self.C)
        self.A = result & 0xFF
        self.set_ZN(self.A)

        self.C = 1 if result >= 0 else 0
        self.O = (a^b) & 0b10000000 != 0 and (a^self.A) & 0b10000000 != 0


    def SEC(self, address, mode):
        self.C = True

    def SED(self, address, mode):
        self.D = True

    def SEI(self, address, mode):
        self.I = True

    def STA(self, address, mode):
        self.memory.store(address, self.A)

    def STX(self, address, mode):
        self.memory.store(address, self.X)

    def STY(self, address, mode):
        self.memory.store(address, self.Y)

    def TAX(self, address, mode):
        self.X = self.A
        self.set_ZN(self.X)

    def TAY(self, address, mode):
        self.Y = self.A
        self.set_ZN(self.Y)

    def TSX(self, address, mode):
        self.X = self.sp
        self.set_ZN(self.X)

    def TXA(self, address, mode):
        self.A = self.X
        self.set_ZN(self.A)

    def TXS(self, address, mode):
        self.sp = self.X

    def TYA(self, address, mode):
        self.A = self.Y
        self.set_ZN(self.A)
