; Each entry structured as such:
; Word $4XY0 "NAME", where X is the page number, Y is the entry number, and NAME is the program name not longer than 13 characters
; Data $4XYE $hh $ll, where $hh is the high address and $ll is the low address

Word $8000 "hello"
Data $800E $10 $00

Word $8010 "names_jond"
Data $801E $11 $00

Word $8020 "list"
Data $802E $16 $00

Word $8030 "count"
Data $803E $18 $00

Word $8040 "DD16"
Data $804E $21 $00

Word $8050 "fib16"
Data $805E $22 $00

Word $8060 "clear"
Data $806E $23 $00

Word $8070 "dump"
Data $807E $26 $00

Word $8080 "cmp_chk"
Data $808E $30 $00

Byte $8090 $80
