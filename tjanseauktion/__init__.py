from .ui import UI

import curses


def run():
    try:
        UI()
    except KeyboardInterrupt:
        curses.endwin()
        curses.reset_shell_mode()