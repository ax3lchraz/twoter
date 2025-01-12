
Line $0400

Label LOOP

Load Acc with Indirect Xhl
Compare with Indirect Yhl

Jump if Not Zero to Label UNEQUAL

Compare with #0
Increment Xhl
Increment Yhl
Jump if Not Zero to Label LOOP
Load Xh with #1
Return

Label UNEQUAL

Load Xh with #0
Return
