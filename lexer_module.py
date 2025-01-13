import enum

class Token:
    def __init__(self, token_value, token_kind):
        self.value = token_value
        self.kind = token_kind

    @staticmethod
    def check_keyword(token_value):
        for kind in TokenType:
            if kind.name == token_value and 100 <= kind.value <= 200:
                return kind
        return None

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    DEC_NUMBER = 1
    HEX_NUMBER = 2
    HEX_ADDRESS = 3
    STRING = 4
    USER_VAL = 5
    

    ADD = 101
    SUBTRACT = 102
    COMPARE = 103
    AND = 104
    OR = 105
    XOR = 106
    NOT = 107
    INVERT = 158
    INCREMENT = 108
    DECREMENT = 109
    ROTATE = 145
    SHIFT = 146
    RIGHT = 147
    LEFT = 148
    LOAD = 110
    STORE = 111
    MOVE = 112
    NOP = 113
    CLEAR = 114
    HALT = 115
    JUMP = 116
    SUBROUTINE = 117
    RETURN = 118
    PUSH = 119
    POP = 120

    CARRY = 121
    BORROW = 122
    
    ACC = 123
    SP = 124
    PC = 125
    XH = 126
    XL = 127
    XHL = 128
    YH = 129
    YL = 130
    YHL = 131
    H = 132
    L = 133
    HL = 134

    ZERO = 135
    INTERRUPT = 136
    NEGATIVE = 151
    FLAGS = 150
    IF = 157

    ABSOLUTE = 137
    INDIRECT = 138
    PAGED = 139
    IMMEDIATE = 140

    LABEL = 141
    VECTOR = 142
    CONSTANT = 143
    LINE = 144
    WORD = 152
    DATA = 159
    BYTE = 160
    LIST = 161
    

    AT = 153
    WITH = 154
    TO = 155
    INTO = 156
    
    MINUS = 201

whitespace = [" ", "\t", "\r"]
ignore_chars = [" ", "\n", "\0"]

class Lexer:

    def __init__(self, source):
        self.source = source.upper() + "\n"
        self.preserved_text = source
        self.current_char = ""
        self.current_pos = -1
        self.next_char()

    def next_char(self):
        self.current_pos += 1
        if self.current_pos >= len(self.source):
            self.current_char = "\0"
        else:
            self.current_char = self.source[self.current_pos]

    def peek(self):
        if self.current_pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.current_pos+1]

    def abort(self, message):
        raise Exception(f"\nLexing Error: {message}\n")
        
    def skip_whitespace(self):
        while self.current_char in whitespace:
            self.next_char()

    def skip_comment(self):
        if self.current_char == ";":
            while self.current_char != "\n":
                self.next_char()

    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()
        token = None

        if self.current_char == "\n":
            token = Token(self.current_char, TokenType.NEWLINE)
        elif self.current_char == "\0":
            token = Token(self.current_char, TokenType.EOF)
        elif self.current_char == "-":
            token = Token(self.current_char, TokenType.MINUS)
        elif self.current_char == "#":
            token = Token(self.current_char, TokenType.IMMEDIATE)
        elif self.current_char == "@":
            token = Token(self.current_char, TokenType.ABSOLUTE)
        elif self.current_char == "_":
            token = Token(self.current_char, TokenType.PAGED)
        elif self.current_char == "*":
            token = Token(self.current_char, TokenType.VECTOR)
        elif self.current_char == ".":
            token = Token(self.current_char, TokenType.LABEL)
        elif self.current_char == "+":
            token = Token(self.current_char, TokenType.CONSTANT)
        elif self.current_char == "=":
            token = Token(self.current_char, TokenType.LINE)
        elif self.current_char == "~":
            token = Token(self.current_char, TokenType.WORD)
        elif self.current_char == ":":
            token = Token(self.current_char, TokenType.BYTE)
        elif self.current_char == ",":
            token = Token(self.current_char, TokenType.LIST)
        elif self.current_char == "?":
            token = Token(self.current_char, TokenType.IF)
        elif self.current_char == "!":
            token = Token(self.current_char, TokenType.NOT)
        elif self.current_char == "\"":
            
            self.next_char()
            start_pos = self.current_pos

            while self.current_char != "\"":
                self.next_char()

            string_value = self.preserved_text[start_pos:self.current_pos]
            token = Token(string_value, TokenType.STRING)
            
        elif self.current_char == "$":

            self.next_char()
            start_pos = self.current_pos

            while self.peek() in "0123456789ABCDEF":
                self.next_char()

            if self.peek() not in ignore_chars:
                self.abort("Invalid Character in Hex Value: " + self.peek())

            hex_value = self.source[start_pos:self.current_pos + 1]
            
            if len(hex_value) <= 2:
                token = Token(hex_value, TokenType.HEX_NUMBER)
            elif len(hex_value) <=4 :
                token = Token(hex_value, TokenType.HEX_ADDRESS)
            else:
                self.abort("Hex Value Out of Range: " + hex_value)
                
        elif self.current_char.isdigit():

            start_pos = self.current_pos

            while self.peek().isdigit():
                self.next_char()

            if self.peek() not in ignore_chars:
                self.abort("Invalid Character in Number: " + self.peek())

            dec_value = self.source[start_pos:self.current_pos + 1]

            if 0 <= int(dec_value) <= 255:
                token = Token(dec_value, TokenType.DEC_NUMBER)
            else:
                self.abort("Decimal Value Out of Range: " + dec_value)

        elif self.current_char.isalpha():

            start_pos = self.current_pos
            while self.peek().isalnum() or self.peek() =="_":
                self.next_char()

            value = self.source[start_pos:self.current_pos + 1]
            keyword = Token.check_keyword(value)
            if keyword == None:
                token = Token(value, TokenType.USER_VAL)
            else:
                token = Token(value, keyword)
            
        else:
            
            self.abort("Unknown Token: " + self.current_char)
            

        self.next_char()
        return token
