from enum import Enum
from memory import Memory

class InterruptType(Enum):
    interruptNone = 1
    interruptNMI = 2
    interruptIRQ = 3

class AddressingMode(Enum):
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

INSTRUCTION_FUNC = [
    CPU.BRK, CPU.ORA, CPU.KIL, CPU.SLO, CPU.NOP, CPU.ORA, CPU.ASL, CPU.SLO,
	CPU.PHP, CPU.ORA, CPU.ASL, CPU.ANC, CPU.NOP, CPU.ORA, CPU.ASL, CPU.SLO,
	CPU.BPL, CPU.ORA, CPU.KIL, CPU.SLO, CPU.NOP, CPU.ORA, CPU.ASL, CPU.SLO,
	CPU.CLC, CPU.ORA, CPU.NOP, CPU.SLO, CPU.NOP, CPU.ORA, CPU.ASL, CPU.SLO,
	CPU.JSR, CPU.AND, CPU.KIL, CPU.RLA, CPU.BIT, CPU.AND, CPU.ROL, CPU.RLA,
	CPU.PLP, CPU.AND, CPU.ROL, CPU.ANC, CPU.BIT, CPU.AND, CPU.ROL, CPU.RLA,
	CPU.BMI, CPU.AND, CPU.KIL, CPU.RLA, CPU.NOP, CPU.AND, CPU.ROL, CPU.RLA,
	CPU.SEC, CPU.AND, CPU.NOP, CPU.RLA, CPU.NOP, CPU.AND, CPU.ROL, CPU.RLA,
	CPU.RTI, CPU.EOR, CPU.KIL, CPU.SRE, CPU.NOP, CPU.EOR, CPU.LSR, CPU.SRE,
	CPU.PHA, CPU.EOR, CPU.LSR, CPU.ALR, CPU.JMP, CPU.EOR, CPU.LSR, CPU.SRE,
	CPU.BVC, CPU.EOR, CPU.KIL, CPU.SRE, CPU.NOP, CPU.EOR, CPU.LSR, CPU.SRE,
	CPU.CLI, CPU.EOR, CPU.NOP, CPU.SRE, CPU.NOP, CPU.EOR, CPU.LSR, CPU.SRE,
	CPU.RTS, CPU.ADC, CPU.KIL, CPU.RRA, CPU.NOP, CPU.ADC, CPU.ROR, CPU.RRA,
	CPU.PLA, CPU.ADC, CPU.ROR, CPU.ARR, CPU.JMP, CPU.ADC, CPU.ROR, CPU.RRA,
	CPU.BVS, CPU.ADC, CPU.KIL, CPU.RRA, CPU.NOP, CPU.ADC, CPU.ROR, CPU.RRA,
	CPU.SEI, CPU.ADC, CPU.NOP, CPU.RRA, CPU.NOP, CPU.ADC, CPU.ROR, CPU.RRA,
	CPU.NOP, CPU.STA, CPU.NOP, CPU.SAX, CPU.STY, CPU.STA, CPU.STX, CPU.SAX,
	CPU.DEY, CPU.NOP, CPU.TXA, CPU.XAA, CPU.STY, CPU.STA, CPU.STX, CPU.SAX,
	CPU.BCC, CPU.STA, CPU.KIL, CPU.AHX, CPU.STY, CPU.STA, CPU.STX, CPU.SAX,
	CPU.TYA, CPU.STA, CPU.TXS, CPU.TAS, CPU.SHY, CPU.STA, CPU.SHX, CPU.AHX,
	CPU.LDY, CPU.LDA, CPU.LDX, CPU.LAX, CPU.LDY, CPU.LDA, CPU.LDX, CPU.LAX,
	CPU.TAY, CPU.LDA, CPU.TAX, CPU.LAX, CPU.LDY, CPU.LDA, CPU.LDX, CPU.LAX,
	CPU.BCS, CPU.LDA, CPU.KIL, CPU.LAX, CPU.LDY, CPU.LDA, CPU.LDX, CPU.LAX,
	CPU.CLV, CPU.LDA, CPU.TSX, CPU.LAS, CPU.LDY, CPU.LDA, CPU.LDX, CPU.LAX,
	CPU.CPY, CPU.CMP, CPU.NOP, CPU.DCP, CPU.CPY, CPU.CMP, CPU.DEC, CPU.DCP,
	CPU.INY, CPU.CMP, CPU.DEX, CPU.AXS, CPU.CPY, CPU.CMP, CPU.DEC, CPU.DCP,
	CPU.BNE, CPU.CMP, CPU.KIL, CPU.DCP, CPU.NOP, CPU.CMP, CPU.DEC, CPU.DCP,
	CPU.CLD, CPU.CMP, CPU.NOP, CPU.DCP, CPU.NOP, CPU.CMP, CPU.DEC, CPU.DCP,
	CPU.CPX, CPU.SBC, CPU.NOP, CPU.ISC, CPU.CPX, CPU.SBC, CPU.INC, CPU.ISC,
	CPU.INX, CPU.SBC, CPU.NOP, CPU.SBC, CPU.CPX, CPU.SBC, CPU.INC, CPU.ISC,
	CPU.BEQ, CPU.SBC, CPU.KIL, CPU.ISC, CPU.NOP, CPU.SBC, CPU.INC, CPU.ISC,
	CPU.SED, CPU.SBC, CPU.NOP, CPU.ISC, CPU.NOP, CPU.SBC, CPU.INC, CPU.ISC,
]

class CPU:
    def __init__(self):
        self.memory = Memory.create()
        self.cycles = 0
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
        flags |= self.B << 4
        flags |= self.O << 6
        flags |= self.N << 7
        return flags

    def setFlags(self, flags):
        self.C = (flags >> 0) & 1
        self.Z = (flags >> 1) & 1
        self.I = (flags >> 2) & 1
        self.D = (flags >> 3) & 1
        self.B = (flags >> 4) & 1
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
        step_cycles = 0
        
        if mode == AddressingMode.modeAbsolute:
            arg = self.read_uint16(self.pc + 1)
        elif mode == AddressingMode.modeAbsoluteX:
            uint16_address = self.read_uint16(self.pc + 1)
            uint8_index_register = self.X

            arg = uint16_address + uint8_index_register
            page_crossed = self._does_addition_carry(uint16_address, uint8_index_register)
        elif mode == AddressingMode.modeAbsoluteY:
            uint16_address = self.read_uint16(self.pc + 1)
            uint8_index_register = self.Y

            arg = uint16_address + uint8_index_register
            page_crossed = self._does_addition_carry(uint16_address, uint8_index_register)
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
        elif mode == AddressingMode.modeIndirect
            # Same bug
            arg = self.read_uint16(self.read_uint16(self.pc + 1))
        elif mode == AddressingMode.modeIndirectIndexed:
            # Warning, there's a bug, the addition with X does not carry. TODO Need to be implemented
            arg = self.read_uint16(self.read_uint16(self.pc + 1)) + self.Y
            page_crossed = self._does_addition_carry(arg - self.Y, address)
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
        step_cycles += INSTRUCTION_CYCLES[opcode]

        if page_crossed:
            step_cycles += INSTRUCTION_PAGE_CYCLES[opcode]
        
        self.execute_instruction(opcode, arg, mode)
        
    def execute_instruction(opcode, address, mode):
        self.INSTRUCTION_FUNC[opcode](address, mode)
    
    @staticmethod
    def _does_addition_carry(big, small):
        return 0xFF00 & (big + small) != 0xFF00 & big

        
        

        
    def set_N(self, val):
        # sets negative flag if val negative (bit 7 set)
        self.N = 1 if value & 0x80 else 0

    def set_Z(self, val):
        # sets zero flag if val is 0
        self.Z = 1 if value == 0 else 0

    def set_ZN(self, val):
        self.set_Z(val)
        self.set_N(val)

    def and(address, mode):
        self.A = self.A & self.read_uint8(address)
        self.set_ZN(self.A)

    def asl(address, mode):
        if mode == AddressingMode.modeAccumulator:
            self.C = (self.A >> 7) & 1
            self.A = (self.A <<= 1) & 0xff # force register to stay on 8 bits
            self.setZN(self.A)
