; fib16 in Two-Ter User Program Table

Vector DD $2000
Constant NEW_LINE 10

Line $2200

Load Xh with Immediate 0
Load Xl with Immediate 1
Load Yh with Immediate 0
Load Yl with Immediate 0

Label LOOP

Push Xh
Push Xl
Push Yh
Push Yl 

Subroutine Vector DD
Load Acc with Constant NEW_LINE
Store Acc at Paged $01

Pop Yl
Pop Yh 
Pop Xl
Pop Xh

Move Xl to Acc
Add Yl
Move Xl to Yl
Move Acc to Xl

Move Xh to Acc
Add with Carry to Yh
Move Xh to Yh
Move Acc to Xh

Return if Carry
Jump to Label LOOP

Word display $2280 "This is a test of the string."