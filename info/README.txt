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
toggles the clock. To toggle the light panel, press the Numpad
'+' key.

Running code and setting up memory is fairly simple. The
contents of mem.txt are loaded into the computer's memory
when reset. If you change this file, you'll have to reset the
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