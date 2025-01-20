; Data Section

; Standard System Vectors

Vector SUB_PROMPT $0300
Vector SUB_DISPLAY $0380
Vector SUB_RUN $0F00
Vector SUB_GET_TOKEN $3100
Vector SUB_RESET_TOKEN $3180
Vector SUB_STR_MATCH $0400
Vector SUB_STR_COPY $0420
Vector SUB_BIN2HEX $2400

; Applicable locally

Constant QMK $3F
Constant SPC $20
Constant BKS $08
Constant NWL $0A

Constant START_PAGE $A0
Vector CURRENT_PAGE $16F0
Vector CURRENT_BYTE $16F1

Word TO_DISP $16C0 "\n    NAME         EXT  PG\n"

; Program Section

Line $1600

Load H with #$16
Load L with #$C0

Subroutine *SUB_DISPLAY
Subroutine *SUB_GET_TOKEN

Load Xh with Constant START_PAGE
Load Xl with #$00

Load Acc with #$A0
Store Acc at *CURRENT_PAGE

Load Acc with #$00
Store Acc at *CURRENT_BYTE

Label MAIN_LOOP

; Initial Checks

Load Acc with *CURRENT_PAGE
Compare with Xh
Jump if Not Zero to .EXIT

Load Acc with #128
Compare with Indirect Xhl
Jump if Zero to .EXIT

; Filter Section

Load Acc with Absolute $7E00
Compare with #0
Jump if Zero to .DISPLAY_ENTRY

Move Xh into Yh
Move Xl into Acc
Add #14
Move Acc into Yl

Load Acc with Absolute $7E00
Compare with Indirect Yhl

Jump if Zero to .DISPLAY_ENTRY

Move Xl into Acc
Add #$10
Move Acc into Xl

Jump if Carry to .EXIT
Jump to .MAIN_LOOP

Label DISPLAY_ENTRY

; Prepare Output

Load Acc with Constant NWL
Store Acc at Paged $01

Load Acc with Constant SPC
Store Acc at Paged $01
Store Acc at Paged $01
Store Acc at Paged $01
Store Acc at Paged $01

Label DISPLAY_LOOP_NAME

Load Acc with Indirect Xhl
Compare with #0
Jump if Not Zero to .SKIP_FIX

; Add $20 to 0, makes it a space

Add Constant SPC
Label SKIP_FIX
Store Acc at Paged $01
Increment Xhl

Load Acc with *CURRENT_BYTE
Increment Acc
Store Acc at *CURRENT_BYTE
Compare to #14
Jump if Not Zero to .DISPLAY_LOOP_NAME

Load Acc with #0
Store Acc at *CURRENT_BYTE

Load Acc with Indirect Xhl
Store Acc at Paged $01
Increment Xhl

Load Acc with Constant SPC
Store Acc at Paged $01
Store Acc at Paged $01
Store Acc at Paged $01

Push Xh
Load Acc with Indirect Xhl
Move Acc into Xh
Subroutine *SUB_BIN2HEX
Pop Xh
Increment Xhl

Jump to .MAIN_LOOP

Label EXIT

Load Acc with Constant NWL
Store Acc at Paged $01
Store Acc at Paged $01
Return
