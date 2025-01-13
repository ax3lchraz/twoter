; Data Section

; Standard System Vectors

Vector SUB_PROMPT $0300
Vector SUB_DISPLAY $0380
Vector SUB_RUN $0F00
Vector SUB_GET_TOKEN $3100
Vector SUB_RESET_TOKEN $3180
Vector SUB_STR_MATCH $0400
Vector SUB_STR_COPY $0420

; Applicable locally

Constant START_PAGE $A0
Constant CMP_STR_PAGE $7E
Constant FILTER_CHAR $43

Vector CURRENT_PAGE $0FF0
Vector CURRENT_BYTE $0FF1
Vector PAGE_BYTE $0FFD

; Program Section

Line $0F00

Load Acc with Constant START_PAGE
Store Acc at Vector CURRENT_PAGE
Load Acc with Immediate 0
Store Acc at Vector CURRENT_BYTE

Label MAIN_LOOP

Load Xh with Vector CURRENT_PAGE
Load Xl with Vector CURRENT_BYTE

Load Acc with Constant START_PAGE ; Still in the page?
Compare with Xh
Jump if Not Zero to .NOT_FOUND

Load Acc with #$80 ; End of the entries?
Compare with Indirect Xhl
Jump if Zero to .NOT_FOUND

Load Yh with Constant CMP_STR_PAGE
Load Yl with #0
Subroutine *SUB_STR_MATCH

Load Acc with *CURRENT_BYTE
Add Immediate $0E
Move Acc into L
Load H with *CURRENT_PAGE
Load Acc with Indirect HL
Compare with Constant FILTER_CHAR
Jump if Zero to .SKIP_SET_XH_0
Load Xh with #0

Label SKIP_SET_XH_0

Increment HL
Load Xl with Indirect HL
Increment HL

Store H at Vector CURRENT_PAGE
Store L at Vector CURRENT_BYTE

Load Acc with #1
Compare to Xh
Jump if Zero to .FOUND
Jump to .MAIN_LOOP

Label NOT_FOUND

Load H with #$0F
Load L with #$C0
Subroutine *SUB_DISPLAY
Return

Line $0FF9

Label FOUND

Store Xl at *PAGE_BYTE
Subroutine $0200
Return

Word $0FC0 "Program Not Found.\n"