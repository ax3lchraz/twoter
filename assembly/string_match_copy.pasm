
Line $0400

Label MATCH_LOOP

Load Acc with Indirect Xhl
Compare with Indirect Yhl

Jump if Not Zero to .UNEQUAL

Compare with #0
Increment Xhl
Increment Yhl
Jump if Not Zero to .MATCH_LOOP
Load Xh with #1
Return

Label UNEQUAL

Load Xh with #0
Return

Line $0420

Label COPY_LOOP

Load Acc with Indirect Xhl
Store Acc at Indirect Yhl
Compare with #0
Return if Zero
Increment Xhl
Increment Yhl
Jump to .COPY_LOOP
