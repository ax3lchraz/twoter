; Veectors and Constants Section

Vector SUB_DISPLAY $0380
Vector SUB_PROMPT $0300

Constant ITER $10
Constant SPACE $20
Constant EOT 0

Byte POINTER_HIGH $31F0 $7F
Byte POINTER_LOW $31F1 $00

; Program Section

Line $3100

Label GET_TOKEN

Load Xh with Vector POINTER_HIGH
Load Xl with Vector POINTER_LOW
Load Yh with Immediate $7E
Load Yl with Immediate $00

Label GET_TOKEN_LOOP

Load Acc with Indirect Xhl
Increment Xhl

Compare with Constant SPACE
Jump if Zero to Label EXIT

Decrement Xhl ; Done to fix positioning at end of statement

Compare with Constant EOT
Jump if Zero to Label EXIT

Increment Xhl

Store Acc at Indirect Yhl
Increment Yhl

Jump to Label GET_TOKEN_LOOP

Label EXIT

Store Xh at Vector POINTER_HIGH
Store Xl at Vector POINTER_LOW

Load Acc with #0
Store Acc at Indirect Yhl

Return

Line $3180

Label RESET_TOKEN_POINTER

Load Acc #$7F
Store Acc Vector POINTER_HIGH
Load Acc #$00
Store Acc Vector POINTER_LOW

Return
