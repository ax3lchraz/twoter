from lexer_module import *
from parser_module import *

asm_file_ext = "pasm"

def main(user_input):

    f = None

    try:
        f = open(f"{__file__}/../assembly/{user_input}.{asm_file_ext}", "r")
    except:
        print(f"\n{user_input}.{asm_file_ext} Not Found\n")
        return

    print("=== SOURCE FILE ===\n")
    source = f.read()
    print(source)
    f.close()

    print("\n=== LEXER ===\n")

    preview = Lexer(source)

    while not preview.current_char == "\0":
        current_token = preview.get_token().kind
        print(current_token.name, end=" ")
        if current_token == TokenType.NEWLINE:
            print("")

    print("\n=== PARSER ===\n")

    f = open(f"{__file__}/../programs/{user_input}.txt", "w")
    
    lexer = Lexer(source)
    parser = Parser(lexer, f)

    compiled_program, _ = parser.program()

    for item in compiled_program:
        f.write(item)
    
    f.close()

    print("\n\nCompiling successful.")

def start():
    stay = True

    while stay:

        user_input = input("? ")
        if user_input in ["", "q", "quit"]: stay = False
        else:
            try:
                main(user_input)
            except Exception as e:
                print(e)

start()
