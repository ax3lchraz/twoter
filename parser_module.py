from lexer_module import *

eight_bit_register_list = [TokenType.XH, TokenType.XL, TokenType.YH, TokenType.YL, TokenType.H, TokenType.L, TokenType.ACC, TokenType.SP]
eight_bit_register_reference = {"XH":"0","XL":"1","YH":"2","YL":"3","H":"4","L":"5","ACC":"6","SP":"7",}

prepositions = [TokenType.WITH, TokenType.AT, TokenType.TO, TokenType.INTO]

class Parser:

    def __init__(self, lexer, operating_file):
        self.lexer = lexer
        self.lexer_copy = lexer

        self.current_token = None
        self.peek_token = None
        
        self.next_token()
        self.next_token()
        self.extended = False
        self.current_line = ""
        self.counter = 0

        self.labels_declared = {}
        self.labels_used = []
        self.vectors_declared = {}
        self.vectors_used = []
        self.constants_declared = {}
        self.constants_used = []

        self.to_append = []
        self.program_list = []
        self.f = operating_file

    def check_token(self, kind):
        if type(kind) == list:
            return self.current_token.kind in kind
        else:
            return kind == self.current_token.kind

    def check_peek(self, kind):
        if type(kind) == list:
            return self.peek_token.kind in kind
        else:
            return kind == self.peek_token.kind

    def match_token(self, kind):
        if not self.check_token(kind):
            if type(kind) == list:
                self.abort("Expected " + ", ".join(str(item.name) for item in kind) + ", got " + self.current_token.kind.name)
            else:
                self.abort("Expected " + kind.name + ", got " + self.current_token.kind.name)

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message):
        raise Exception(f"Parser Error: {message}")

    def new_line(self):
        
        self.next_token()
        self.match_token(TokenType.NEWLINE)

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    def program(self):

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        while not self.check_token(TokenType.EOF):
            self.statement()

        print("\nLABELS\n")

        for item in self.labels_declared.keys():
            print(f"{item}: {self.labels_declared[item][0]} {self.labels_declared[item][1]}")

        print("\nVECTORS\n")

        for item in self.vectors_declared.keys():
            print(f"{item}: {self.vectors_declared[item][0]} {self.vectors_declared[item][1]}")

        print("\nCONSTANTS\n")

        for item in self.constants_declared.keys():
            print(f"{item}: {self.constants_declared[item]}")

        for item in self.labels_used:
            if item not in self.labels_declared.keys(): self.abort(f"Label {item} used but not declared")

        for item in self.vectors_used:
            if item not in self.vectors_declared.keys(): self.abort(f"Vector {item} used but not declared")

        for item in self.constants_used:
            if item not in self.constants_declared.keys(): self.abort(f"Constant {item} used but not declared")

        counter = 0

        return_list = []
        return_debug_list = []

        for line in range(len(self.program_list)):

            if len(self.program_list[line]) == 0:
                continue

            hex_counter = hex(counter)[2:].zfill(4)
            print(f"\n{hex_counter} : ", end="")
            counter += len(self.program_list[line])
            return_debug_list.append(f"{hex_counter} : ")

            for item in range(len(self.program_list[line])):

                check_item = self.program_list[line][item]

                if check_item.startswith("ln"):
                    counter = int(check_item[2:], 16)

                for label, value in self.labels_declared.items():

                    if f"{label}_H" == check_item:
                        self.program_list[line][item] = value[0]
                    elif f"{label}_L" == check_item:
                        self.program_list[line][item] = value[1]

                for vector, value in self.vectors_declared.items():

                    if f"{vector}_H" == check_item:
                        self.program_list[line][item] = value[0]
                    elif f"{vector}_L" == check_item:
                        self.program_list[line][item] = value[1]

                for constant, value in self.constants_declared.items():

                    if f"{constant}" == check_item:
                        self.program_list[line][item] = value

                print(f"{self.program_list[line][item]}", end=" ")
                return_list.append(f"{self.program_list[line][item]} ")
                return_debug_list.append(f"{self.program_list[line][item]} ")

            return_list.append("\n")
            return_debug_list.append("\n")

        return return_list, return_debug_list

    def variable(self, opcode):

        self.counter += 3
        
        self.to_append.append(opcode)
        self.to_append.append(f"{self.current_token.value}_H")
        self.to_append.append(f"{self.current_token.value}_L")

    def string_to_data(self, hex_address, string_value):

        self.counter = int(hex_address, 16)
        self.to_append.append(f"ln{hex_address}")
        self.to_append.append("\n\n")

        position = 0
        backslash = False
        for character in string_value:
            self.counter += 1

            value = ord(character)

            if value == 92:
                backslash = True
                continue
            
            if backslash and value == 110:
                backslash = False
                value = 10

            self.to_append.append(f"0x{hex(value)[2:].zfill(2)}")

            position += 1

            if position % 4 == 0: self.to_append.append("\t")
            if position % 16 == 0: self.to_append.append("\n")
            if position % 64 == 0: self.to_append.append("\n")
            if position % 256 == 0: self.to_append.append("\n\n\n")

        self.to_append.append("\n\n")


    def absolute_address(self, opcode):

        self.counter += 3
        
        addr_hex = self.current_token.value
        addr_high_hex = f"0x{addr_hex[0:2]}"
        addr_low_hex = f"0x{addr_hex[2:4]}"

        self.to_append.append(opcode)
        self.to_append.append(addr_high_hex)
        self.to_append.append(addr_low_hex)

    def paged_address(self, opcode):

        self.counter += 2

        addr_hex = self.current_token.value
        self.to_append.append(opcode)
        self.to_append.append(f"0x{addr_hex}")

    def immediate(self, opcode):

        self.counter += 2
        self.to_append.append(opcode)
        constant_value = None

        if self.check_token(TokenType.HEX_NUMBER):

            constant_value = f"0x{self.current_token.value}"

        elif self.check_token(TokenType.MINUS):

            self.next_token()
            self.match_token(TokenType.DEC_NUMBER)

            constant_value = str((~int(self.current_token.value)) + 1)

        elif self.check_token(TokenType.DEC_NUMBER):

            constant_value = self.current_token.value

        elif self.check_token(TokenType.USER_VAL):

            constant_value = self.current_token.value
            self.constants_used.append(constant_value)

        else:
            
            self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        self.to_append.append(constant_value)

    def statement(self):

        self.extended = False
        self.current_line = ""

        self.to_append = []

        counter_hex = hex(self.counter)[2:].zfill(4)
        counter_high_hex = f"0x{counter_hex[0:2]}"
        counter_low_hex = f"0x{counter_hex[2:4]}"

        # LINE HEX_ADDRESS
        if self.check_token(TokenType.LINE):
            
            self.next_token()
            self.match_token(TokenType.HEX_ADDRESS)
            self.counter = int(self.current_token.value, 16)
            self.to_append.append(f"ln{self.current_token.value}")

        # LABEL USER_VAL
        elif self.check_token(TokenType.LABEL):
            
            self.next_token()
            self.match_token(TokenType.USER_VAL)

            if self.current_token.value in self.labels_declared: self.abort(f"Label {self.current_token.value} already exists in program.")

            self.labels_declared[self.current_token.value] = [counter_high_hex, counter_low_hex]

        # VECTOR USER_VAL HEX_ADDRESS
        elif self.check_token(TokenType.VECTOR):
            
            self.next_token()
            self.match_token(TokenType.USER_VAL)

            if self.current_token.value in self.vectors_declared: self.abort(f"Vector {self.current_token.value} already exists in program.")

            active_value = self.current_token.value
            
            self.next_token()
            self.match_token(TokenType.HEX_ADDRESS)

            addr_hex = self.current_token.value
            addr_high_hex = f"0x{addr_hex[0:2]}"
            addr_low_hex = f"0x{addr_hex[2:4]}"
            self.vectors_declared[active_value] = [addr_high_hex, addr_low_hex]

        # CONSTANT USER_VAL ( HEX_NUMBER | [MINUS] DEC_NUMBER )
        elif self.check_token(TokenType.CONSTANT):

            self.next_token()
            self.match_token(TokenType.USER_VAL)

            if self.current_token.value in self.constants_declared: self.abort(f"Constant {self.current_token.value} already exists in program.")

            constant_name = self.current_token.value
            constant_value = None

            self.next_token()

            if self.check_token(TokenType.HEX_NUMBER):

                constant_value = f"0x{self.current_token.value}"

            elif self.check_token(TokenType.MINUS):

                self.next_token()
                self.match_token(TokenType.DEC_NUMBER)

                constant_value = str((~int(self.current_token.value)) + 1)

            elif self.check_token(TokenType.DEC_NUMBER):

                constant_value = self.current_token.value

            else:
                
                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.constants_declared[constant_name] = constant_value
            
        # DATA [ USER_VAL ] HEX_ADDRESS ( HEX_NUMBER | [MINUS] DEC_NUMBER )
        elif self.check_token(TokenType.DATA):
        
            self.next_token()
            
            if self.check_token(TokenType.USER_VAL):
            
                if self.current_token.value in self.vectors_declared: self.abort(f"Vector {self.current_token.value} already exists in program.")

                vector_name = self.current_token.value

                self.next_token()
                self.match_token(TokenType.HEX_ADDRESS)

                addr_hex = self.current_token.value
                addr_high_hex = f"0x{addr_hex[0:2]}"
                addr_low_hex = f"0x{addr_hex[2:4]}"
                self.vectors_declared[vector_name] = [addr_high_hex, addr_low_hex]
                
                self.to_append.append(f"ln{addr_hex}")

                self.next_token()
                if self.check_token(TokenType.HEX_NUMBER):

                    self.to_append.append(f"0x{self.current_token.value}")

                elif self.check_token(TokenType.MINUS):

                    self.next_token()
                    self.match_token(TokenType.DEC_NUMBER)

                    self.to_append.append(str((~int(self.current_token.value)) + 1))

                elif self.check_token(TokenType.DEC_NUMBER):

                    self.to_append.append(self.current_token.value)

                else:
                    
                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")
                
            elif self.check_token(TokenType.HEX_ADDRESS):
            
                addr_hex = self.current_token.value
                addr_high_hex = f"0x{addr_hex[0:2]}"
                addr_low_hex = f"0x{addr_hex[2:4]}"
                self.vectors_declared[vector_name] = [addr_high_hex, addr_low_hex]
                
                self.to_append.append(f"ln{addr_hex}")

                self.next_token()
                if self.check_token(TokenType.HEX_NUMBER):

                    self.to_append.append(f"0x{self.current_token.value}")

                elif self.check_token(TokenType.MINUS):

                    self.next_token()
                    self.match_token(TokenType.DEC_NUMBER)

                    self.to_append.append(str((~int(self.current_token.value)) + 1))

                elif self.check_token(TokenType.DEC_NUMBER):

                    self.to_append.append(self.current_token.value)

                else:
                    
                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")
                
            else:
            
                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        # WORD [USER_VAL] HEX_ADDRESS STRING
        elif self.check_token(TokenType.WORD):
            
            self.next_token()
            
            if self.check_token(TokenType.USER_VAL):

                if self.current_token.value in self.vectors_declared: self.abort(f"Vector {self.current_token.value} already exists in program.")

                vector_name = self.current_token.value

                self.next_token()
                self.match_token(TokenType.HEX_ADDRESS)

                addr_hex = self.current_token.value
                addr_high_hex = f"0x{addr_hex[0:2]}"
                addr_low_hex = f"0x{addr_hex[2:4]}"
                self.vectors_declared[vector_name] = [addr_high_hex, addr_low_hex]

                self.next_token()
                self.match_token(TokenType.STRING)

                string_value = self.current_token.value

                self.string_to_data(addr_hex, string_value)

            elif self.check_token(TokenType.HEX_ADDRESS):

                addr_hex = self.current_token.value
                addr_high_hex = f"0x{addr_hex[0:2]}"
                addr_low_hex = f"0x{addr_hex[2:4]}"

                self.next_token()
                self.match_token(TokenType.STRING)

                string_value = self.current_token.value

                self.string_to_data(addr_hex, string_value)

            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        # DATA [ USER_VAL ] HEX_ADDRESS ( HEX_NUMBER | [MINUS] DEC_NUMBER )
        elif self.check_token(TokenType.DATA):
        
            self.next_token()
            
            if self.check_token(TokenType.USER_VAL):
            
                if self.current_token.value in self.vectors_declared: self.abort(f"Vector {self.current_token.value} already exists in program.")

                vector_name = self.current_token.value

                self.next_token()
                self.match_token(TokenType.HEX_ADDRESS)

                addr_hex = self.current_token.value
                addr_high_hex = f"0x{addr_hex[0:2]}"
                addr_low_hex = f"0x{addr_hex[2:4]}"
                self.vectors_declared[vector_name] = [addr_high_hex, addr_low_hex]
                
                self.to_append.append(f"ln{addr_hex}")

                self.next_token()
                if self.check_token(TokenType.HEX_NUMBER):

                    self.to_append.append(f"0x{self.current_token.value}")

                elif self.check_token(TokenType.MINUS):

                    self.next_token()
                    self.match_token(TokenType.DEC_NUMBER)

                    self.to_append.append(str((~int(self.current_token.value)) + 1))

                elif self.check_token(TokenType.DEC_NUMBER):

                    self.to_append.append(self.current_token.value)

                else:
                    
                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")


        #HALT
        elif self.check_token(TokenType.HALT):

            self.to_append.append("0o070")

        # CLEAR ( CARRY | NEGATIVE | ZERO | INTERRUPT | FLAGS )
        elif self.check_token(TokenType.CLEAR):

            block = "0"
            column = "0"

            self.counter += 1
            self.next_token()

            if self.check_token(TokenType.CARRY): row = "1"
            elif self.check_token(TokenType.NEGATIVE): row = "2"
            elif self.check_token(TokenType.ZERO): row = "3"
            elif self.check_token(TokenType.INTERRUPT): row = "4"
            elif self.check_token(TokenType.FLAGS): row = "5"
            else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # INCREMENT [ ACC | XHL | YHL | HL ]
        elif self.check_token(TokenType.INCREMENT):

            block = "0"
            self.counter += 1
            
            if self.check_peek(TokenType.NEWLINE):
                row = "0"
                column = "7"
            elif self.check_peek(TokenType.ACC):
                self.next_token()
                row = "0"
                column = "7"
            elif self.check_peek(TokenType.XHL):
                self.next_token()
                row = "0"
                column = "6"
            elif self.check_peek(TokenType.YHL):
                self.next_token()
                row = "2"
                column = "6"
            elif self.check_peek(TokenType.HL):
                self.next_token()
                row = "4"
                column = "6"
            else:
                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # DECREMENT [ ACC | XHL | YHL | HL ]
        elif self.check_token(TokenType.DECREMENT):

            block = "0"
            self.counter += 1
            
            if self.check_peek(TokenType.NEWLINE):
                row = "1"
                column = "7"
            elif self.check_peek(TokenType.ACC):
                self.next_token()
                row = "1"
                column = "7"
            elif self.check_peek(TokenType.XHL):
                self.next_token()
                row = "1"
                column = "6"
            elif self.check_peek(TokenType.YHL):
                self.next_token()
                row = "3"
                column = "6"
            elif self.check_peek(TokenType.HL):
                self.next_token()
                row = "5"
                column = "6"
            else:
                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # INVERT [ ACC ]
        elif self.check_token(TokenType.INVERT):

            block = "0"
            self.counter += 1

            if self.check_peek(TokenType.NEWLINE):
                row = "6"
                column = "7"
            elif self.check_peek(TokenType.ACC):
                self.next_token()
                row = "6"
                column = "7"
            else:
                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # ( ROTATE | SHIFT ) [ ACC ] ( RIGHT | LEFT )
        elif self.check_token([TokenType.ROTATE, TokenType.SHIFT]):

            block = "0"
            self.counter += 1

            offset = 0
            if self.check_token(TokenType.SHIFT): offset = 2

            self.next_token()
            if self.check_token(TokenType.ACC):
                self.next_token()

            if self.check_token(TokenType.RIGHT):
                row = str(2 + offset)
                column = "7"
            elif self.check_token(TokenType.LEFT):
                row = str(3 + offset)
                column = "7"
            else:
                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # ( PUSH | POP ) ( XH | XL | YH | YL | H | L | ACC | SP | XHL | YHL | HL ) 
        elif self.check_token([TokenType.PUSH, TokenType.POP]):

            block = "0"

            if self.check_peek(eight_bit_register_list):

                self.counter += 1
                
                offset = 0
                if self.check_token(TokenType.POP): offset = 1

                self.next_token()

                column = str(4 + offset)
                row = eight_bit_register_reference[self.current_token.kind.name]

            elif self.check_peek([TokenType.XHL, TokenType.YHL, TokenType.HL, TokenType.PC]):

                self.counter += 2
                self.to_append.append("0o060")
                column = "7"

                offset = 0
                if self.check_token(TokenType.POP): offset = 1

                self.next_token()
                if self.check_token(TokenType.XHL): offset += 0
                elif self.check_token(TokenType.YHL): offset += 2
                elif self.check_token(TokenType.HL): offset += 4
                elif self.check_token(TokenType.PC): offset += 6
                else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

                row = str(offset)

            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # ( JUMP | SUBROUTINE ) [ IF ( ( [NOT] ( CARRY | NEGATIVE | ZERO ) ) | INTERRUPT ) ] [ TO | AT ] ( HEX_ADDRESS | LABEL USER_VAL | VECTOR USER_VAL )
        elif self.check_token([TokenType.JUMP, TokenType.SUBROUTINE]):

            block = "0"
            column = "1"
            offset = 0
            if self.check_token(TokenType.SUBROUTINE): column = "2"

            self.next_token()
            if self.check_token(TokenType.IF):

                self.next_token()
                if self.check_token(TokenType.NOT):
                    if self.check_peek(TokenType.INTERRUPT): self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")
                    self.next_token()
                    offset = 3
                
                if self.check_token(TokenType.CARRY): offset += 1
                elif self.check_token(TokenType.NEGATIVE): offset += 2
                elif self.check_token(TokenType.ZERO): offset += 3
                elif self.check_token(TokenType.INTERRUPT): offset = 7
                else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

                self.next_token()

            row = str(offset)

            if self.check_token([TokenType.TO, TokenType.AT]):
                self.next_token()

            if self.check_token(TokenType.LABEL):

                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.labels_used.append(self.current_token.value)
                self.variable(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.VECTOR):

                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.vectors_used.append(self.current_token.value)
                self.variable(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.HEX_ADDRESS):

                self.absolute_address(f"0o{block}{row}{column}")

            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        # RETURN [ IF ( ( [NOT] ( CARRY | NEGATIVE | ZERO ) ) | INTERRUPT ) ]
        elif self.check_token(TokenType.RETURN):

            block = "0"
            column = "3"
            offset = 0

            if self.check_peek(TokenType.IF):

                self.next_token()
                self.next_token()
                if self.check_token(TokenType.NOT):
                    if self.check_peek(TokenType.INTERRUPT): self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")
                    self.next_token()
                    offset = 3
                
                if self.check_token(TokenType.CARRY): offset += 1
                elif self.check_token(TokenType.NEGATIVE): offset += 2
                elif self.check_token(TokenType.ZERO): offset += 3
                elif self.check_token(TokenType.INTERRUPT): offset = 7
                else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            row = str(offset)

            self.to_append.append(f"0o{block}{row}{column}")

        # MOVE ( XH | XL | YH | YL | H | L | ACC | SP | XHL | YHL | HL ) [ WITH | AT | TO | INTO ] ( XH | XL | YH | YL | H | L | ACC | SP | XHL | YHL | HL )
        elif self.check_token(TokenType.MOVE):

            block = "3"
            self.next_token()
            if self.check_token(eight_bit_register_list):

                self.counter += 1

                column = eight_bit_register_reference[self.current_token.kind.name]
                self.next_token()

                if self.check_token(prepositions):
                    self.next_token()

                self.match_token(eight_bit_register_list)
                row = eight_bit_register_reference[self.current_token.kind.name]

            elif self.check_token([TokenType.XHL, TokenType.YHL, TokenType.HL]):

                self.counter += 2

                block = "0"
                column = "6"
                self.to_append.append("0o060")

                if self.check_token(TokenType.HL):

                    self.next_token()

                    if self.check_token(prepositions):
                        self.next_token()

                    if self.check_token(TokenType.XHL): row = "1"
                    elif self.check_token(TokenType.YHL): row = "3"
                    else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

                elif self.check_token(TokenType.XHL):

                    self.next_token()

                    if self.check_token(prepositions):
                        self.next_token()

                    if self.check_token(TokenType.HL): row = "4"
                    elif self.check_token(TokenType.YHL): row = "2"
                    else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

                elif self.check_token(TokenType.YHL):

                    self.next_token()

                    if self.check_token(prepositions):
                        self.next_token()

                    if self.check_token(TokenType.HL): row = "5"
                    elif self.check_token(TokenType.XHL): row = "0"
                    else: self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

                else:

                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            self.to_append.append(f"0o{block}{row}{column}")

        # LOAD (XH | XL | YH | YL | H | L | ACC | SP) [ WITH | AT | TO | INTO ] ( VECTOR USER_VAL | ABSOLUTE HEX_ADDRESS | PAGED HEX_NUMBER | INDIRECT (HL | XHL | YHL) | IMMEDIATE ( HEX_NUMBER | [MINUS] DEC_NUMBER ) | CONSTANT USER_VAL )
        elif self.check_token(TokenType.LOAD):

            block = "2"
            self.next_token()
            self.match_token(eight_bit_register_list)
            row = eight_bit_register_reference[self.current_token.kind.name]

            self.next_token()

            if self.check_token(prepositions):
                self.next_token()

            if self.check_token(TokenType.VECTOR):

                column = "0"

                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.vectors_used.append(self.current_token.value)
                self.variable(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.ABSOLUTE):

                column = "0"

                self.next_token()
                self.match_token(TokenType.HEX_ADDRESS)
                self.absolute_address(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.PAGED):

                column = "1"

                self.next_token()
                self.match_token(TokenType.HEX_NUMBER)
                self.paged_address(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.INDIRECT):

                self.next_token()

                if self.check_token(TokenType.HL):

                    self.counter += 1
                    column = "2"
                    self.to_append.append(f"0o{block}{row}{column}")

                elif self.check_token(TokenType.XHL):

                    self.counter += 2
                    block = "0"
                    column = "2"
                    self.to_append.append("0o060")
                    self.to_append.append(f"0o{block}{row}{column}")

                elif self.check_token(TokenType.YHL):

                    self.counter += 2
                    block = "0"
                    column = "3"
                    self.to_append.append("0o060")
                    self.to_append.append(f"0o{block}{row}{column}")

                else:

                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            elif self.check_token(TokenType.IMMEDIATE):

                column = "3"
                self.next_token()
                self.immediate(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.CONSTANT):

                column = "3"
                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.immediate(f"0o{block}{row}{column}")

            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        # STORE ( XH | XL | YH | YL | H | L | ACC | SP ) [ WITH | AT | TO | INTO ] ( VECTOR USER_VAL | ABSOLUTE HEX_ADDRESS | PAGED HEX_NUMBER | INDIRECT ( HL | XHL | YHL ) )
        elif self.check_token(TokenType.STORE):

            block = "2"
            self.next_token()
            self.match_token(eight_bit_register_list)
            row = eight_bit_register_reference[self.current_token.kind.name]

            self.next_token()

            if self.check_token(prepositions):
                self.next_token()

            if self.check_token(TokenType.VECTOR):

                column = "4"

                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.vectors_used.append(self.current_token.value)
                self.variable(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.ABSOLUTE):

                column = "4"

                self.next_token()
                self.match_token(TokenType.HEX_ADDRESS)
                self.absolute_address(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.PAGED):

                column = "5"

                self.next_token()
                self.match_token(TokenType.HEX_NUMBER)
                self.paged_address(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.INDIRECT):

                self.next_token()

                if self.check_token(TokenType.HL):

                    self.counter += 1
                    column = "6"
                    self.to_append.append(f"0o{block}{row}{column}")

                elif self.check_token(TokenType.XHL):

                    self.counter += 2
                    block = "0"
                    column = "4"
                    self.to_append.append("0o060")
                    self.to_append.append(f"0o{block}{row}{column}")

                elif self.check_token(TokenType.YHL):

                    self.counter += 2
                    block = "0"
                    column = "5"
                    self.to_append.append("0o060")
                    self.to_append.append(f"0o{block}{row}{column}")

                else:

                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")


            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        # ( ADD [ [WITH] CARRY ] | SUBTRACT [ [WITH] BORROW ] | COMPARE | AND | OR | XOR ) [ WITH | AT | TO | INTO ] ( VECTOR USER_VAL | ABSOLUTE HEX_ADDRESS | PAGED HEX_NUMBER | INDIRECT (HL | XHL | YHL) | IMMEDIATE ( HEX_NUMBER | [MINUS] DEC_NUMBER ) | CONSTANT USER_VAL | XH | XL | YH | YL )
        elif self.check_token([TokenType.ADD, TokenType.SUBTRACT, TokenType.COMPARE, TokenType.AND, TokenType.OR, TokenType.XOR]):

            block = "1"

            if self.check_token(TokenType.ADD):

                row = "0"
                self.next_token()

                if self.check_token(prepositions):
                    self.next_token()

                if self.check_token(TokenType.CARRY):
                    row = "1"
                    self.next_token()
                
            elif self.check_token(TokenType.SUBTRACT):

                row = "2"
                self.next_token()

                if self.check_token(prepositions):
                    self.next_token()

                if self.check_token(TokenType.BORROW):
                    row = "3"
                    self.next_token()

            elif self.check_token(TokenType.COMPARE):

                row = "4"
                self.next_token()

            elif self.check_token(TokenType.AND):

                row = "5"
                self.next_token()

            elif self.check_token(TokenType.OR):

                row = "6"
                self.next_token()

            elif self.check_token(TokenType.XOR):

                row = "7"
                self.next_token()

            if self.check_token(prepositions):
                self.next_token()

            if self.check_token(TokenType.VECTOR):

                column = "0"

                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.vectors_used.append(self.current_token.value)
                self.variable(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.ABSOLUTE):

                column = "0"

                self.next_token()
                self.match_token(TokenType.HEX_ADDRESS)
                self.absolute_address(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.PAGED):

                column = "1"

                self.next_token()
                self.match_token(TokenType.HEX_NUMBER)
                self.paged_address(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.INDIRECT):

                self.next_token()

                if self.check_token(TokenType.HL):

                    self.counter += 1
                    column = "2"
                    self.to_append.append(f"0o{block}{row}{column}")

                elif self.check_token(TokenType.XHL):

                    self.counter += 2
                    block = "0"
                    column = "0"
                    self.to_append.append("0o060")
                    self.to_append.append(f"0o{block}{row}{column}")

                elif self.check_token(TokenType.YHL):

                    self.counter += 2
                    block = "0"
                    column = "1"
                    self.to_append.append("0o060")
                    self.to_append.append(f"0o{block}{row}{column}")

                else:

                    self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

            elif self.check_token(TokenType.IMMEDIATE):

                column = "3"
                self.next_token()
                self.immediate(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.CONSTANT):

                column = "3"
                self.next_token()
                self.match_token(TokenType.USER_VAL)
                self.immediate(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.XH):

                column = "4"
                self.to_append.append(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.XL):

                column = "5"
                self.to_append.append(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.YH):

                column = "6"
                self.to_append.append(f"0o{block}{row}{column}")

            elif self.check_token(TokenType.YL):

                column = "7"
                self.to_append.append(f"0o{block}{row}{column}")

            else:

                self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")


        else:

            self.abort("Invalid Statement: " + self.current_token.value + " (" + self.current_token.kind.name + ")")

        self.program_list.append(self.to_append)
        self.new_line()
