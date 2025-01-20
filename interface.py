from curses import *
from sim import *

twoter = computer()

panel = """
┌─────────────────────────────┬─────────────────┬──────────────────────────────────────────┐
│         The Two-Ter         │ x Keyboard Mode │ Last Input:                              │
├──────────────────┬──────────┼─────────────────┴──────────────────────────────────────────┤
│ ╒══SP══╕╒══IR══╕ │ ╒═STEP═╕ │                                                            │
│ xxxxxxxxxxxxxxxx │ xxxxxxxx │                                                            │
│ ╒══════PC══════╕ │ ╒═FLGS═╕ │                                                            │
│ xxxxxxxxxxxxxxxx │ CxZxNxIx │                                                            │
├──────────────────┼──────────┤                                                            │
│ ╒══Xh══╕╒══Xl══╕ │ ╒S CTRL╕ │                                                            │
│ xxxxxxxxxxxxxxxx │ xxxxxxxx │                                                            │
│ ╒══Yh══╕╒══Yl══╕ │          │                                                            │
│ xxxxxxxxxxxxxxxx │ 1 STEP x │                                                            │
│ ╒══════HL══════╕ ├──────────┤                                                            │
│ xxxxxxxxxxxxxxxx │          │                                                            │
│ ╒══Th══╕╒══Tl══╕ │          │                                                            │
│ xxxxxxxxxxxxxxxx │          │                                                            │
├──────────────────┼──────────┤                                                            │
│ ╒══AC══╕╒═DATA═╕ │ ╒MEMORY╕ │                                                            │
│ xxxxxxxxxxxxxxxx │ RDX WRTX │                                                            │
│ ╒═════ADDR═════╕ │ ╒═CLCK═╕ │                                                            │
│ xxxxxxxxxxxxxxxx │ CxAxBxRx │                                                            │
├──────────────────┼──────────┤                                                            │
│ ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ │ ●●●●▼ ●● │                                                            │
└──────────────────┴──────────┴────────────────────────────────────────────────────────────┘
"""

def mem_dump(data):
    file = open("dump.txt", "w")

    for page in range(0,256):

        file.write(f"\nPage: {str(hex(page))[2:]}")

        for row in range(0,16):

            file.write("\n    ")
            
            for column in range(0,16):

                addr = (page << 8) + (row << 4) + column

                write_num = str(hex(data[addr]))[2:] + " "
                if len(write_num) == 2: write_num = f"0{write_num}"

                file.write(write_num)

    file.close()
    

#└ ┐ ┘ ┌  ┤ ├ ┴ ┬ ┼ ─ │ ▲ ▼ ●
def update_panel(stdscr, k_mode, terminal_y, terminal_x, current_user_in, terminal_lines, full_disp, current_speed):

    twoter.update()

    if twoter.ab == 1 and twoter.mem_wt:
        user_input = twoter.memory[1]
        if user_input > 0:
            stdscr.addstr(2, 62, "              ")
            stdscr.addstr(2, 66, str(user_input))

        if 32 <= user_input <= 126 and terminal_x <= 90:
            stdscr.addstr(terminal_y, terminal_x, chr(user_input), color_pair(10))
            stdscr.addstr(2, 62, chr(user_input))
            current_user_in += chr(user_input)
            terminal_x += 1
        elif user_input == 8 and terminal_x > 32:
            current_user_in = current_user_in[0:len(current_user_in)-1]
            stdscr.addstr(2, 62, "BK")
            terminal_x -= 1
        if user_input == 10 or terminal_x == 90:
            terminal_lines.append(current_user_in)
            stdscr.addstr(2, 62, "LF")
            current_user_in = ""
            terminal_x = 32
            stdscr.addstr(terminal_y, terminal_x, "                                                           ")

            for index in range(4, 23):
                stdscr.addstr(index, 32, "                                                           ")
                stdscr.addstr(index, 32, terminal_lines[index + (len(terminal_lines)-23)], color_pair(10))

    stdscr.addstr(terminal_y, terminal_x, "█ ", color_pair(10))
    
    """
    stdscr.addstr(10, 21, str(twoter.reg_Xh)+"  ", color_pair(2))
    stdscr.addstr(10, 25, str(twoter.reg_Xl)+"  ", color_pair(6))
    stdscr.addstr(10, 32, str(twoter.reg_Xhl)+"    ", color_pair(3))

    stdscr.addstr(12, 21, str(twoter.reg_Yh)+"  ", color_pair(6))
    stdscr.addstr(12, 25, str(twoter.reg_Yl)+"  ", color_pair(2))
    stdscr.addstr(12, 32, str(twoter.reg_Yhl)+"    ", color_pair(3))

    stdscr.addstr(14, 21, str(twoter.reg_HL)+"    ", color_pair(5))

    stdscr.addstr(16, 21, str(twoter.reg_Th)+"  ", color_pair(2))
    stdscr.addstr(16, 25, str(twoter.reg_Tl)+"  ", color_pair(6))
    stdscr.addstr(16, 32, str(twoter.reg_Thl)+"    ", color_pair(3))
    """

    # Show K Mode regardless of screen update

    if k_mode:
        stdscr.addstr(2, 32, "●", color_pair(2))
    else:
        stdscr.addstr(2, 32, "○", color_pair(2))

    if not full_disp:
        return terminal_y, terminal_x, current_user_in, terminal_lines, full_disp
    
    # [is_on, y_pos, x_pos, color]
    single_lights = [
        [twoter.clock, 21, 22, 2],
        [twoter.phase_A, 21, 24, 3],
        [twoter.phase_B, 21, 26, 3],
        [twoter.run, 21, 28, 2],
        [twoter.carry, 7, 22, 2],
        [twoter.zero, 7, 24, 2],
        [twoter.negative, 7, 26, 2],
        [twoter.interrupt, 7, 28, 2],
        [twoter.mem_rd, 19, 23, 2],
        [twoter.mem_wt, 19, 28, 2],
        [twoter.single_step, 12, 28, 6]
    ]

    for light in single_lights:

        is_on = light[0]
        y_pos = light[1]
        x_pos = light[2]
        color = light[3]

        if is_on:
            stdscr.addstr(y_pos, x_pos, "●", color_pair(color))
        else:
            stdscr.addstr(y_pos, x_pos, "○", color_pair(color))

    # [value, bit_len, y_pos, x_pos, color]
    group_lights = [
        [twoter.sp, 8, 5, 2, 6],
        [twoter.ir, 8, 5, 10, 2],
        [twoter.pc, 16, 7, 2, 5],
        [twoter.reg_Xh, 8, 10, 2, 2],
        [twoter.reg_Xl, 8, 10, 10, 6],
        [twoter.reg_Yh, 8, 12, 2, 6],
        [twoter.reg_Yl, 8, 12, 10, 2],
        [twoter.reg_HL, 16, 14, 2, 5],
        [twoter.reg_Th, 8, 16, 2, 2],
        [twoter.reg_Tl, 8, 16, 10, 6],
        [twoter.ac, 8, 19, 2, 6],
        [twoter.db, 8, 19, 10, 2],
        [twoter.ab, 16, 21, 2, 5],
        [twoter.rc, 8, 5, 21, 2],
        [2 ** current_speed, 8, 10, 21, 2]
    ]

    for light in group_lights:

        value = light[0]
        check = light[1]
        init_check = check
        y_pos = light[2]
        x_pos = light[3]
        color = light[4]

        while check > 0:

            check -= 1
            diff = value - (2 ** check)
            
            if diff >= 0:
                stdscr.addstr(y_pos, x_pos, "●", color_pair(color))
                value = diff
            else:
                stdscr.addstr(y_pos, x_pos, "○", color_pair(color))

            x_pos += 1
    
    
    return terminal_y, terminal_x, current_user_in, terminal_lines, full_disp
            
def main(stdscr):
    stdscr.clear()
    stdscr.keypad(1)
    stdscr.nodelay(1)
    noecho()
    #halfdelay(1)
    curs_set(0)

    start_color()

    init_color(128, 1000, 800, 0)
    
    init_pair(1, COLOR_BLACK, COLOR_BLACK)
    init_pair(2, COLOR_RED, COLOR_BLACK)
    init_pair(3, COLOR_GREEN, COLOR_BLACK)
    init_pair(4, COLOR_BLUE, COLOR_BLACK)
    init_pair(5, COLOR_CYAN, COLOR_BLACK)
    init_pair(6, COLOR_YELLOW, COLOR_BLACK)
    init_pair(7, COLOR_MAGENTA, COLOR_BLACK)
    init_pair(8, COLOR_WHITE, COLOR_BLACK)
    init_pair(10, 128, COLOR_BLACK)
    
    exit = False
    k_mode = True
    cycle = 0
    full_disp = True

    current_user_in = ""
    terminal_lines = ["" for _ in range(0, 23)]
    terminal_x = 32
    terminal_y = 23

    twoter.reset()
    twoter.run = True

    stdscr.addstr(panel)

    current_speed = 0
    max_speed = 7
    speed_step = 0

    terminal_y, terminal_x, current_user_in, terminal_lines, full_disp = update_panel(stdscr, k_mode, terminal_y, terminal_x, current_user_in, terminal_lines, full_disp, current_speed)
    stdscr.refresh()

    full_disp = True
    
    while not exit:
        last_input = stdscr.getch()

        if last_input == 27: # Escape Key
            exit = True
        elif last_input == 32 and k_mode == False: # Space Key
            if twoter.run:
                twoter.run = False
            else:
                twoter.run = True
                twoter.clock = True
        elif last_input == 114 and k_mode == False: # r Key
            twoter.reset()
            twoter.mem_refresh()
        elif last_input == 115 and not k_mode: # s Key
            current_speed += 1
            if current_speed > max_speed:
                current_speed = 0
        elif last_input == 116 and not k_mode: #t Key
            twoter.single_step = ~twoter.single_step
        elif last_input == 96: # ` Key, Keyboard Mode
            k_mode = not k_mode
        elif last_input == 459:
            mem_dump(twoter.memory)
        elif last_input == 465:
            full_disp = not full_disp
        elif k_mode and last_input > 0:
            twoter.memory[0] = last_input

        speed_step += 1
        if speed_step >= 2 ** current_speed:
            speed_step = 0
            terminal_y, terminal_x, current_user_in, terminal_lines, full_disp = update_panel(stdscr, k_mode, terminal_y, terminal_x, current_user_in, terminal_lines, full_disp, current_speed)
            
        stdscr.refresh()

    endwin()

wrapper(main)
