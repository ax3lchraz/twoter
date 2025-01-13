; Data Section

Vector SUB_PROMPT $0300
Vector SUB_DISPLAY $0380
Vector SUB_RUN $0F00
Vector SUB_GET_TOKEN $3100
Vector SUB_RESET_TOKEN $3180
Vector SUB_STR_MATCH $0400
Vector SUB_STR_COPY $0420

Byte INPUT_STRING_STORE_PAGE $0370 $7F

Word $7F00 "Two-Ter User Utility v0\n\n"

; Program Section

Line $0200

Label ENTRY

Load H with #$7F
Load L with #$00

Subroutine Vector SUB_DISPLAY

Label LOOP

Subroutine Vector SUB_PROMPT
Subroutine Vector SUB_RESET_TOKEN
Subroutine Vector SUB_GET_TOKEN
Subroutine Vector SUB_RUN

Jump to Label LOOP