; Data Section

Constant QMK $3F
Constant SPC $20
Constant BKS $08
Constant NWL $0A

Vector STORE_PAGE $0370

; Program Section

Line $0300

Load H with *STORE_PAGE
Load L with #$00
Load Acc with Constant QMK
Store Acc at Paged $01
Load Acc with Constant SPC
Store Acc at Paged $01

Label FETCH_INPUT

Load Acc with Paged $00
Compare to #0
Jump if Zero to .FETCH_INPUT
Load Xh with #0
Store Xh at Paged $00
Move Acc into Xh
Compare to Constant BKS
Jump if Not Zero to .NOT_BACKSPACE
Move L into Acc
Compare to #0
Jump if Zero to .FETCH_INPUT
Decrement HL
Store Xh at Paged $01
Jump to .FETCH_INPUT

Label NOT_BACKSPACE

Compare to Constant NWL
Jump if Zero to .REGISTER
Compare to #126
Jump if Not Negative to .FETCH_INPUT
Compare to #32
Jump if Negative to .FETCH_INPUT

Label REGISTER

Store Xh at Paged $01
Store Xh at Indirect HL
Increment HL
Compare to Constant NWL
Jump if Not Zero to .FETCH_INPUT
Decrement HL
Load Acc with #0
Store Acc at Indirect HL
Return

Line $0380

Label ECHO_LOOP

Load Acc with Indirect HL
Compare to #0
Return if Zero
Store Acc at Paged $01
Increment HL
Jump to .ECHO_LOOP
