; Each entry structured as such:
; Word $4XY0 "NAME", where X is the page number, Y is the entry number, and NAME is the program name not longer than 13 characters
; Data $4XYE $hh $ll, where $hh is the high address and $ll is the low address

Word $4000 "hello"
Data $400E $10 $00

Word $4010 "names_jond"
Data $401E $11 $00

Word $4020 "list"
Data $402E $16 $00

Word $4030 "count"
Data $403E $18 $00

Word $4040 "DD16"
Data $404E $21 $00

Word $4050 "fib16"
Data $405E $22 $00

Word $4060 "clear"
Data $406E $23 $00

Word $4070 "dump"
Data $407E $26 $00

Word $4080 "cmp_chk"
Data $408E $30 $00

Byte $4090 $80
