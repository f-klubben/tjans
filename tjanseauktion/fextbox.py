import curses
from curses.textpad import Textbox

from typing import Optional, Callable


class Fextbox(Textbox):
    """
    I had issues with not being able to use backspace to delete in Textboxes, as the default
    backspace key (263) does not match my own. This also allows us to define custom behaviour
    of different key inputs when editing the text fields in the UI.

    Any additional key behaviour should be added between the START / END comments in Fextbox.edit()
    """
    BACKSPACE = [263, 127]
    ESC = 27

    def __init__(self, win, insert_mode=False):
        super(Fextbox, self).__init__(win, insert_mode=insert_mode)

    def edit(self, validate: Optional[Callable[[int], int]] = None) -> str:
        while 1:
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            # START custom behaviour
            if ch in self.BACKSPACE:
                if not self.do_command(curses.KEY_BACKSPACE):
                    break
            if ch == self.ESC:
                return ''
            # END custom behaviour
            if not self.do_command(ch):
                break
            self.win.refresh()
        return self.gather()
