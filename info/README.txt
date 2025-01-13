Hello and welcome!

To get started with the Two-Ter emulator, you'll need to
install the windows-curses module for Python 3.12 or any
version compatible with 3.12.

To install the module, run this command:

pip install windows-curses

Or visit https://pypi.org/project/windows-curses/ if you
have issues with the installation.

Furthermore, the emulator won't run from within the IDE,
so run this command in the Windows terminal to start it:

python /../twoter/interface.py

Now the emulator should be up and running!

Be default, the computer will be running from address
$0200 and in Keyboard Mode. To toggle Keyboard Mode, press
the ` key. Pressing r will reset the computer, and Space
toggles the clock. To toggle the light panel, press the
Numpad + key. NOTICE: Disabling the light panel also
disables the Keyboad Mode indicator. The s key will
cycle through speed modes, the speed being divided by
the number shown on S CTRL. The t key toggles Single
Step mode, which halts the computer after the
complete execution of one instruction.

Running code and setting up memory is fairly simple. The
contents of the text files in the 'programs' directory
are loaded into the computer's memory when reset. If you
change this file, you'll have to reset the
computer to load it.

Furthermore, when loading memory, new lines and whitespace are
treated as the same thing, so this:

0o001 0x7f 0x00

is equivalent to this:

0o001
0x7f
0x00

If you want to jump to a specific line, simply type 'ln'
followed by the hex address. For example, to jump to line
$0200, type ln0200.

As for the compiler, I included the pseudo assembly UDL for
Notepad ++. It's not required for programming in the pseudo
assembly language, it's just the best way I could find to get
the syntax highlighting I wanted with ease. MAKE SURE YOUR
ASSEMBLY FILES END IN .pasm! Either that, or change asm_file_ext
in compiler.py to something else like txt.

If you wanna see what programs are already set up, type and enter
'list.' The dump and DD16 commands take one command line argument,
dump requiring a two digit hex number, and DD16 requiring a four
digit hex number. 'dump 20' will display the memory contents at
page 20, i.e. 0x2000-0x20FF. DD16 FFFF will output 65535.
