; Data section

Vector DISPLAY $0380
Word TO_DISPLAY $30C0 "\nThis is a test of the compiler.\n\nIf this string is being displayed, it's working perfectly.\n"
Constant TO_DISPLAY_ADDR_H $30
Constant TO_DISPLAY_ADDR_L $C0

; Program section

Line $3000

Load H with Constant TO_DISPLAY_ADDR_H
Load L with Constant TO_DISPLAY_ADDR_L
Subroutine Vector DISPLAY

Return
