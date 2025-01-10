from random import *
from math import log
import os

bsc_addr_mode = {
    "00":"none",
    "01":"abs",
    "02":"abs",
    "03":"none",
    "04":"none",
    "05":"none",
    "06":"none",
    "07":"none",
    "10":"abs",
    "11":"zpg",
    "12":"hl",
    "13":"imm",
    "14":"none",
    "15":"none",
    "16":"none",
    "17":"none",
    "20":"abs",
    "21":"zpg",
    "22":"hl",
    "23":"imm",
    "24":"abs",
    "25":"zpg",
    "26":"hl",
    "27":"none",
    "30":"none",
    "31":"none",
    "32":"none",
    "33":"none",
    "34":"none",
    "35":"none",
    "36":"none",
    "37":"none"
}

ext_addr_mode = {
    "00":"Xhl",
    "01":"Yhl",
    "02":"Xhl",
    "03":"Yhl",
    "04":"Xhl",
    "05":"Yhl",
    "06":"none",
    "07":"none"
}

reset_vector = 0x0200

def num_to_bits(value):

    check = 8
    
    block = (value & 0b11000000) >> 6
    column = (value & 0b00111000) >> 3
    row = value & 0b00000111
    
    active_bits = [False for _ in range(check)]
    
    while check > 0:

        check -= 1
        diff = value - (2 ** check)
    
        if diff >= 0:
            value = diff
            active_bits[check] = True

    return block, column, row, active_bits

def two_comp(num):

    num = ~num + 1
    
    return num

def fetch_mem():

    new_mem = [0 for _ in range(0, 65536)]
    directory = f"{__file__}/../programs"
    counter = 0

    for current_file in os.listdir(directory):

        f = open(f"{__file__}/../programs/{current_file}", "r")
        
        for line in f:
            line = line.split()
            for item in line:
                if item[0:1] == ";":
                    break
                match item[0:2]:
                    case "0b":
                        new_mem[counter] = int(item, 2)
                        counter += 1
                    case "0o":
                        new_mem[counter] = int(item, 8)
                        counter += 1
                    case "0x":
                        new_mem[counter] = int(item, 16)
                        counter += 1
                    case "ln":
                        counter = int(item[2:], 16)
                    case _:
                        new_mem[counter] = int(item)
                        counter += 1

    f.close()

    return new_mem

class computer:

    def __init__(self):

        self.clock = False
        self.phase_A = False
        self.phase_B = True
        self.run = False
        self.single_step = False

        self.carry = False
        self.negative = False
        self.zero = True
        self.interrupt = False
        
        self.memory = [randint(0,255) for addr in range(0, 65536)]
        self.mem_rd = False
        self.mem_wt = False

        self.ac_i = randint(0,255)
        self.ac = randint(0,255)
        self.pc_i = randint(0,65535)
        self.pc = randint(0,65535)
        self.sp_i = randint(0,255)
        self.sp = randint(0,255)
        self.sp_page = (1) << 8
        self.ir = randint(0,255)
        self.rc = 1
        self.rc_rst = False
        self.db = 0
        self.ab = 0
        self.ext = False
        
        self.reg_Xh = randint(0,255)
        self.reg_Xl = randint(0,255)
        self.reg_Yh = randint(0,255)
        self.reg_Yl = randint(0,255)
        self.reg_H = randint(0,255)
        self.reg_L = randint(0,255)
        self.reg_Th = randint(0,255)
        self.reg_Tl = randint(0,255)

        self.reg_Xhl = randint(0,65535)
        self.reg_Yhl = randint(0,65535)
        self.reg_HL = randint(0,65535)
        self.reg_Thl = randint(0,65535)

        self.addr_mode = "none"

    def mem_refresh(self):

        self.memory = fetch_mem()        

    def reset(self):

        self.clock = False
        self.phase_A = False
        self.phase_B = True
        self.run = False
        self.single_step = False

        self.carry = False
        self.negative = False
        self.zero = True
        self.interrupt = False

        self.memory = fetch_mem()
            
        self.mem_rd = False
        self.mem_wt = False

        self.ac_i = 0
        self.ac = 0
        self.pc_i = reset_vector
        self.pc = reset_vector
        self.sp_i = 0
        self.sp = 0
        self.sp_page = (1) << 8
        self.ir = 0
        self.rc = 1
        self.rc_rst = False
        self.db = 0
        self.ab = 0
        self.ext = False

        self.reg_Xh = 0
        self.reg_Xl = 0
        self.reg_Yh = 0
        self.reg_Yl = 0
        self.reg_H = 0
        self.reg_L = 0
        self.reg_Th = 0
        self.reg_Tl = 0

        self.reg_Xhl = 0
        self.reg_Yhl = 0
        self.reg_HL = 0
        self.reg_Thl = 0

        self.addr_mode = "none"

    def update(self):

        if self.clock:
            self.clock = False
        else:
            self.clock = True

        self.reg_Xhl = (self.reg_Xh << 8) | self.reg_Xl
        self.reg_Yhl = (self.reg_Yh << 8) | self.reg_Yl
        self.reg_HL = (self.reg_H << 8) | self.reg_L
        self.reg_Thl = (self.reg_Th << 8) | self.reg_Tl
        self.pc_h = (self.pc & 0xff00) >> 8
        self.pc_l = (self.pc & 0x00ff)

        if not self.run:
            return 0

        # Set proper computer phase
        if not self.clock:

            self.ac = self.ac_i
            self.pc = self.pc_i
            self.sp = self.sp_i
            
            if self.phase_A:
                self.phase_A = False
            else:
                self.phase_A = True

        self.phase_B = not self.phase_A

        A = self.phase_A and self.clock
        B = self.phase_B and self.clock
        
        if B:
            self.rc *= 2
            if self.rc > 128:
                self.rc = 1

            if self.rc_rst:
                self.rc_rst = False
                self.rc = 1

                if self.single_step:
                    self.run = False

        # Reset some control lines and the busses

        if self.phase_B:
            self.mem_rd = False
            self.mem_wt = False

            self.ab = 0
            self.db = 0

        # Everything hereafter executes on phase A
        if not A:
            return 0

        # Fetch cycle
        if self.rc == 1:
            self.pc_i += 1
            if self.pc_i > 65535:
                self.pc_i = 0
            
            self.ab = self.pc
            self.mem_rd = True
            self.db = self.memory[self.ab]
            self.ir = self.db

        # Enable specific control logic if the opcode + column use a common addressing mode
        
        block, row, column, active_bits = num_to_bits(self.ir)

        ref_val = f"{block}{column}"
        
        if self.ext:
            self.addr_mode = ext_addr_mode[ref_val]
        else:
            self.addr_mode = bsc_addr_mode[ref_val]
        
        time_pos = int(log(self.rc, 2))
        
        # Addressing mode shared logic
        
        if self.addr_mode == "abs":
            match time_pos:
                case 1:
                    self.pc_i += 1
                    if self.pc_i > 65535:
                        self.pc_i = 0

                    self.ab = self.pc
                    self.mem_rd = True
                    self.db = self.memory[self.ab]
                    self.reg_Th = self.db
                case 2:
                    self.pc_i += 1
                    if self.pc_i > 65535:
                        self.pc_i = 0
                    
                    self.ab = self.pc
                    self.mem_rd = True
                    self.db = self.memory[self.ab]
                    self.reg_Tl = self.db
                case 3:
                    self.ab = self.reg_Thl
                    

        elif self.addr_mode == "zpg":
            match time_pos:
                case 1:
                    self.pc_i += 1
                    if self.pc_i > 65535:
                        self.pc_i = 0

                    self.ab = self.pc
                    self.mem_rd = True
                    self.db = self.memory[self.ab]
                    self.reg_Tl = self.db
                case 2:
                    self.ab = self.reg_Tl

        elif self.addr_mode == "imm":
            match time_pos:
                case 1:
                    self.pc_i += 1
                    if self.pc_i > 65535:
                        self.pc_i = 0
    
                    self.ab = self.pc
                    self.mem_rd = True
                    self.db = self.memory[self.ab]

        elif self.addr_mode == "hl":
            match time_pos:
                case 1:
                    self.ab = self.reg_HL

        elif self.addr_mode == "Xhl":
            match time_pos:
                case 1:
                    self.ab = self.reg_Xhl

        elif self.addr_mode == "Yhl":
            match time_pos:
                case 1:
                    self.ab = self.reg_Yhl
                    
        # Main Block Logic

        if block == 0 and not self.ext:

            can_jump = (
                (row == 0) or
                (row == 1 and self.carry) or
                (row == 2 and self.negative) or
                (row == 3 and self.zero) or
                (row == 4 and not self.carry) or
                (row == 5 and not self.negative) or
                (row == 6 and not self.zero) or
                (row == 7 and self.interrupt)
            )
            
            match column:
                case 0:
                    if time_pos == 1:
                        match row:
                            case 1:
                                self.carry = False
                            case 2:
                                self.negative = False
                            case 3:
                                self.zero = False
                            case 4:
                                self.interrupt = False
                            case 5:
                                self.carry = False
                                self.negative = False
                                self.zero = False
                                self.interrupt = False
                            case 6:
                                self.ext = True
                            case 7:
                                self.run = False

                        self.rc_rst = True
                                
                case 1:
                    if time_pos == 3:
                        self.rc_rst = True
                        if can_jump:
                            self.pc_i = self.reg_Thl
                            
                case 2:
                    if can_jump:
                        match time_pos:
                            case 4:
                                self.sp_i += 1
                                self.ab = self.sp_page + self.sp
                                self.memory[self.ab] = self.pc_h
                                self.mem_wt = True
                            case 5:
                                self.sp_i += 1
                                self.ab = self.sp_page + self.sp
                                self.memory[self.ab] = self.pc_l
                                self.mem_wt = True
                            case 6:
                                self.ab = self.reg_Thl
                                self.pc_i = self.ab
                                self.rc_rst = True
                    else:
                        if time_pos == 3:
                            self.rc_rst = True

                case 3:
                    if can_jump:
                        match time_pos:
                            case 1:
                                self.sp_i -= 1
                            case 2:
                                self.sp_i -= 1
                                self.ab = self.sp_page + self.sp
                                self.db = self.memory[self.ab]
                                self.reg_Tl = self.db
                                self.mem_rd = True
                            case 3:
                                self.ab = self.sp_page + self.sp
                                self.db = self.memory[self.ab]
                                self.reg_Th = self.db
                                self.mem_rd = True
                            case 4:
                                self.ab = self.reg_Thl
                                self.pc_i = self.ab
                                self.rc_rst = True

                    else:
                        if time_pos == 1:
                            self.rc_rst = True
                            
                case 4:
                    match time_pos:
                        case 1:
                            self.sp_i += 1
                            match row:
                                case 0:
                                    self.db = self.reg_Xh
                                case 1:
                                    self.db = self.reg_Xl
                                case 2:
                                    self.db = self.reg_Yh
                                case 3:
                                    self.db = self.reg_Yl
                                case 4:
                                    self.db = self.reg_H
                                case 5:
                                    self.db = self.reg_L
                                case 6:
                                    self.db = self.ac
                                case 7:
                                    self.db = self.sp

                            self.ab = self.sp_page + self.sp
                            self.memory[self.ab] = self.db
                            self.mem_wt = True
                            self.rc_rst = True
                case 5:
                    match time_pos:
                        case 1:
                            self.sp_i -= 1
                        case 2:

                            self.ab = self.sp_page + self.sp
                            self.db = self.memory[self.ab]
                            self.mem_rd = True
                            
                            match row:
                                case 0:
                                    self.reg_Xh = self.db
                                case 1:
                                    self.reg_Xl = self.db
                                case 2:
                                    self.reg_Yh = self.db
                                case 3:
                                    self.reg_Yl = self.db
                                case 4:
                                    self.reg_H = self.db
                                case 5:
                                    self.reg_L = self.db
                                case 6:
                                    self.ac_i = self.db
                                case 7:
                                    self.sp_i = self.db

                            self.rc_rst = True

                case 6:
                    match time_pos:
                        case 1:
                            if ((not active_bits[5]) and (not active_bits[4])):
                                self.ab = self.reg_Xhl
                            elif ((not active_bits[5]) and active_bits[4]):
                                self.ab = self.reg_Yhl
                            elif (active_bits[5] and (not active_bits[4])):
                                self.ab = self.reg_HL
                                
                            self.reg_Th = (self.ab & 0xff00) >> 8
                            self.reg_Tl = self.ab & 0x00ff
                            
                        case 2:
                            if not active_bits[3]:
                                self.reg_Thl += 1
                                if self.reg_Thl > 65535:
                                    self.reg_Thl = 0
                            else:
                                self.reg_Thl -= 1
                                if self.reg_Thl < 0:
                                    self.reg_Thl = 65535

                            self.ab = self.reg_Thl

                            if ((not active_bits[5]) and (not active_bits[4])):
                                self.reg_Xh = (self.ab & 0xff00) >> 8
                                self.reg_Xl = self.ab & 0x00ff
                            elif ((not active_bits[5]) and active_bits[4]):
                                self.reg_Yh = (self.ab & 0xff00) >> 8
                                self.reg_Yl = self.ab & 0x00ff
                            elif (active_bits[5] and (not active_bits[4])):
                                self.reg_H = (self.ab & 0xff00) >> 8
                                self.reg_L = self.ab & 0x00ff

                            self.rc_rst = True
                            
                case 7:
                    if time_pos == 1:
                        self.rc_rst = True
                        match row:
                            case 0:
                                self.ac_i = self.ac + 1
                            case 1:
                                self.ac_i = self.ac - 1
                            case 2:
                                is_1_set = False
                                if self.ac_i % 2 == 1: is_1_set = True
                                    
                                self.ac_i = self.ac >> 1
                                if self.carry:
                                    self.ac_i += 128

                                if is_1_set: self.carry = True
                            case 3:
                                self.ac_i = self.ac << 1
                                if self.carry:
                                    self.ac_i += 1
                            case 4:
                                is_1_set = False
                                if self.ac_i % 2 == 1: is_1_set = True
                                    
                                self.ac_i = self.ac >> 1
                            case 5:
                                self.ac_i = self.ac << 1
                            case 6:
                                self.ac_i = ~self.ac
                        
                        if self.ac_i > 255:
                            self.ac_i -= 256
                            self.carry = True
                        elif 256 > self.ac_i > 0:
                            self.carry = False
                            self.negative = False
                        elif self.ac_i < 0:
                            self.ac_i = ~self.ac_i + 1
                            self.carry = True
                            self.negative = True
                        elif self.ac_i < 0:
                            self.negative = True

                        if self.ac_i == 0:
                            self.zero = True
                        else:
                            self.zero = False
                     
        if block == 1:

            b_num = 0
            result = 0

            if (column == 0 and time_pos == 3) or (column == 1 and time_pos == 2) or ((column == 2 or column == 3) and time_pos == 1):
                b_num = self.db
                self.rc_rst = True
                self.mem_rd = True

            elif time_pos == 1:
                match column:
                    case 4:
                        self.db = self.reg_Xh
                        b_num = self.db
                    case 5:
                        self.db = self.reg_Xl
                        b_num = self.db
                    case 6:
                        self.db = self.reg_Yh
                        b_num = self.db
                    case 7:
                        self.db = self.reg_Yl
                        b_num = self.db
            
            if (column == 0 and time_pos == 3) or (column == 1 and time_pos == 2) or (2 <= column <= 7 and time_pos == 1):
            
                match row:
                    case 0:
                        result = self.ac + b_num
                    case 1:
                        result = self.ac + b_num + self.carry
                    case 2:
                        result = self.ac - b_num
                    case 3:
                        result = self.ac - b_num - self.carry
                    case 4:
                        result = self.ac - b_num
                    case 5:
                        result = self.ac & b_num
                    case 6:
                        result = self.ac | b_num
                    case 7:
                        result = self.ac ^ b_num

                self.carry = False
                self.negative = False
                self.zero = False
                
                if result > 255:
                    result -= 256
                    self.carry = True
                elif result < 0:
                    result = (~result) + 1
                    self.negative = True

                if result == 0:
                    self.zero = True

                if row != 4:
                    self.ac_i = result
                    
                                
        if block == 2:

            # Load operations

            if (column == 0 and time_pos == 3) or (column == 1 and time_pos == 2) or ((column == 2 or column == 3) and time_pos == 1):
                self.db = self.memory[self.ab]
                self.mem_rd = True
                match row:
                    case 0:
                        self.reg_Xh = self.db
                    case 1:
                        self.reg_Xl = self.db
                    case 2:
                        self.reg_Yh = self.db
                    case 3:
                        self.reg_Yl = self.db
                    case 4:
                        self.reg_H = self.db
                    case 5:
                        self.reg_L = self.db
                    case 6:
                        self.ac_i = self.db
                    case 7:
                        self.sp_i = self.db
                        
                self.rc_rst = True
                        
            # Store operations

            if (column == 4 and time_pos == 3) or (column == 5 and time_pos == 2) or (column == 6 and time_pos == 1):
                self.mem_wt = True
                match row:
                    case 0:
                        self.db = self.reg_Xh
                    case 1:
                        self.db = self.reg_Xl
                    case 2:
                        self.db = self.reg_Yh
                    case 3:
                        self.db = self.reg_Yl
                    case 4:
                        self.db = self.reg_H
                    case 5:
                        self.db = self.reg_L
                    case 6:
                        self.db = self.ac
                    case 7:
                        self.db = self.sp
                        
                self.memory[self.ab] = self.db
                self.rc_rst = True
                        
        # Move operations
        
        elif block == 3:
            
            match time_pos:
                case 1:

                    match column:
                        case 0:
                            self.db = self.reg_Xh
                        case 1:
                            self.db = self.reg_Xl
                        case 2:
                            self.db = self.reg_Yh
                        case 3:
                            self.db = self.reg_Yl
                        case 4:
                            self.db = self.reg_H
                        case 5:
                            self.db = self.reg_L
                        case 6:
                            self.db = self.ac
                        case 7:
                            self.db = self.sp

                    match row:
                        case 0:
                            self.reg_Xh = self.db
                        case 1:
                            self.reg_Xl = self.db
                        case 2:
                            self.reg_Yh = self.db
                        case 3:
                            self.reg_Yl = self.db
                        case 4:
                            self.reg_H = self.db
                        case 5:
                            self.reg_L = self.db
                        case 6:
                            self.ac_i = self.db
                        case 7:
                            self.sp_i = self.db

                    self.rc_rst = True
        
        if block == 0 and self.ext and self.ir != 0o060:
            
            if column in [0, 1, 2, 3, 4, 5] and time_pos == 1:

                self.ext = False
                self.rc_rst = True

                if column in [0, 1]:

                    self.mem_rd = True
                    self.db = self.memory[self.ab]

                    b_num = 0
                    result = 0
                    
                    b_num = self.db
                    self.rc_rst = True
                    
                    match row:
                        case 0:
                            result = self.ac + b_num
                        case 1:
                            result = self.ac + b_num + self.carry
                        case 2:
                            result = self.ac - b_num
                        case 3:
                            result = self.ac - b_num - self.carry
                        case 4:
                            result = self.ac - b_num
                        case 5:
                            result = self.ac & b_num
                        case 6:
                            result = self.ac | b_num
                        case 7:
                            result = self.ac ^ b_num

                    self.carry = False
                    self.negative = False
                    self.zero = False
                    
                    if result > 255:
                        result -= 256
                        self.carry = True
                    elif result < 0:
                        result = (~result) + 1
                        self.negative = True

                    if result == 0:
                        self.zero = True

                    if row != 4:
                        self.ac_i = result
                        
                elif column in [2, 3]:

                    self.mem_rd = True
                    self.db = self.memory[self.ab]

                    match row:
                        case 0:
                            self.reg_Xh = self.db
                        case 1:
                            self.reg_Xl = self.db
                        case 2:
                            self.reg_Yh = self.db
                        case 3:
                            self.reg_Yl = self.db
                        case 4:
                            self.reg_H = self.db
                        case 5:
                            self.reg_L = self.db
                        case 6:
                            self.ac_i = self.db
                        case 7:
                            self.sp_i = self.db

                elif column in [4, 5]:

                    match row:
                        case 0:
                            self.db = self.reg_Xh
                        case 1:
                            self.db = self.reg_Xl
                        case 2:
                            self.db = self.reg_Yh
                        case 3:
                            self.db = self.reg_Yl
                        case 4:
                            self.db = self.reg_H
                        case 5:
                            self.db = self.reg_L
                        case 6:
                            self.db = self.ac
                        case 7:
                            self.db = self.sp

                    self.mem_wt = True
                    self.memory[self.ab] = self.db

            elif column == 6 and time_pos == 1:

                self.ext = False
                self.rc_rst = True

                if row == 0 or row == 5:
                    self.ab = self.reg_Yhl
                elif row == 2 or row == 4:
                    self.ab = self.reg_Xhl
                elif row == 1 or 3:
                    self.ab = self.reg_HL

                upper = (self.ab & 0xf0) >> 8
                lower = self.ab & 0x0f

                if row == 0 or row == 1:
                    self.reg_Xh = upper
                    self.reg_Xl = lower
                elif row == 2 or row == 3:
                    self.reg_Yh = upper
                    self.reg_Xl = lower
                elif row == 4 or row == 5:
                    self.reg_H = upper
                    self.reg_L = lower

            elif column == 7 and not active_bits[3]:

                match time_pos:
                    case 1:
                        
                        self.sp_i += 1
                        if row in [0,1]:
                            self.db = self.reg_Xh
                        elif row in [2,3]:
                            self.db = self.reg_Yh
                        elif row in [4,5]:
                            self.db = self.reg_H
                        else:
                            self.db = self.pc_h

                        self.ab = self.sp_page + self.sp
                        self.memory[self.ab] = self.db
                        self.mem_wt = True
                        
                    case 2:
                        
                        self.sp_i += 1
                        if row in [0,1]:
                            self.db = self.reg_Xl
                        elif row in [2,3]:
                            self.db = self.reg_Yl
                        elif row in [4,5]:
                            self.db = self.reg_L
                        else:
                            self.db = self.pc_l

                        self.ab = self.sp_page + self.sp
                        self.memory[self.ab] = self.db
                        self.mem_wt = True
                        self.rc_rst = True
                        self.ext = False
                        
                        

            elif column == 7 and active_bits[3]:
                
                match time_pos:
                    case 1:
                        self.sp_i -= 1
                    
                    case 2:

                        self.ab = self.sp_page + self.sp
                        self.db = self.memory[self.ab]
                        self.mem_rd = True
                        
                        self.sp_i -= 1
                        if row in [0,1]:
                            self.reg_Xl = self.db
                        elif row in [2,3]:
                            self.reg_Yl = self.db
                        elif row in [4,5]:
                            self.reg_L = self.db
                        else:
                            pc_low = self.db
                        
                    case 3:

                        self.ab = self.sp_page + self.sp
                        self.db = self.memory[self.ab]
                        self.mem_rd = True
                        self.rc_rst = True
                        self.ext = False
                        
                        if row in [0,1]:
                            self.reg_Xh = self.db
                        elif row in [2,3]:
                            self.reg_Yh = self.db
                        elif row in [4,5]:
                            self.reg_H = self.db
                        else:
                            pc_high = self.db
                            self.pc_i = (pc_high << 8) + pc_low

            
                
                
twoter = computer()
