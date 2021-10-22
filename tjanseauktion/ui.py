from . import constants
from . import common
from .config import Config
from .team import Team
from .auction import Auction
from .chore import Chore
from .fextbox import Fextbox
from .validation import InputValidation
from .message import Message
from .logger import MessageLogger, StateLogger
from .output import OutputWriter

import curses
import math
import os
from curses.textpad import rectangle
from typing import Optional, List


class UI:
    WINDOW_TOP_MARGIN = 1
    TITLE = "Tjanseauktion"
    HR = "-" * 40
    HEADER_ELEMS = [
        {'text': TITLE, 'attr': curses.A_UNDERLINE},
        {'text': HR, 'attr': 0},
        {'text': 'auction', 'attr': curses.A_BOLD},
        {'text': 'bid', 'attr': 0},
        {'text': HR, 'attr': 0}
    ]

    CMD_MENU = [
        {'cmd': 'b', 'help': "Edit bid text box"},
        {'help': "<ENTER> to try and place bid"},
        {'help': "<ESC> to cancel"},
        {'help': f"Bid syntax: {InputValidation.BID_PATTERN}"},
        {'help': f"Instant win syntax: {InputValidation.BID_INSTANT_WIN_PATTERN}"},
        {'help': f"Freebie syntax: {InputValidation.BID_FREEBIE_PATTERN}"},
        {'cmd': 'c', 'help': "Edit conversion text box"},
        {'help': "<ENTER> to try and convert"},
        {'help': "<ESC> to cancel"},
        {'help': f"Syntax: {InputValidation.CONVERT_PATTERN}"},
        {'cmd': 's', 'help': "Sell chore to highest bidder"},
        {'cmd': 'r', 'help': "Reset bids for current auction"},
        {'cmd': 'p', 'help': "Revert last auction"}
    ]

    def __init__(self):
        if not os.path.isdir('logs'):
            os.mkdir('logs')

        self.cfg = Config()
        self.msg_logger = MessageLogger()
        self.state_logger = StateLogger()

        if self.state_logger.is_state_log_present():
            self.chores = Chore.load_chores()
            self.teams, self.auctions, self.completed_auctions, self.cur_auction = self.state_logger.load_state()
        else:
            self.teams = [Team(i) for i in range(self.cfg.auction_n_teams())]
            self.chores = Chore.load_chores()
            self.auctions = Auction.create_auctions(self.chores, self.cfg.auction_n_secrets(), len(self.teams))
            self.completed_auctions = []  # type: List[Auction]
            self.cur_auction = self.auctions[0]  # type: Auction
            del self.auctions[0]

        self.window = curses.initscr()

        self.bid_edit_win = None  # would love to type hint, but class is private
        self.bid_box = None  # type: Optional[Fextbox]
        self.convert_edit_win = None  # would love to type hint, but class is private
        self.convert_box = None  # type: Optional[Fextbox]
        self.input_textbox_cols = 20
        self.log_textbox = None  # type: Optional[Fextbox]
        self.log_win = None  # would love to type hint, but class is private
        self.log_textbox_row = 0
        # max amount of messages to keep in UI log
        self.log_textbox_row_limit = 10
        self.log_textbox_cols = 60
        self.log_textbox_msgs = []  # type: List[Message]

        # window row state; ui is generated procedurally
        self.cur_row = self.WINDOW_TOP_MARGIN

        # output msg state; row is set once ui is generated
        self.msg = None  # type: Optional[Message]
        self.msg_output_row = 0

        # stat menu state; set once help text is generated
        self.stat_menu_row = 0

        # legend menu state; set once stat menu is generated
        self.legend_menu_row = 0

        self.n_chores_per_team = math.ceil(len(self.chores) / len(self.teams))

        # ensure terminal supports colours before enabling
        if curses.has_colors():
            curses.start_color()

        # setup colour pairs, (pair_id, foreground, background)
        curses.init_pair(constants.COLOUR_ERR_MSG, curses.COLOR_RED, 0)
        curses.init_pair(constants.COLOUR_SUCCESS_MSG, curses.COLOR_GREEN, 0)

        # don't echo keys on screen
        curses.noecho()
        # react to key inputs without waiting for enter key
        curses.cbreak()
        # hide cursor on screen
        curses.curs_set(0)

        self.draw_ui()
        self.window.refresh()
        self.event_loop()

    def draw_ui(self):
        """
        Procedurally draw terminal UI
        """
        self.draw_help_text()
        self.draw_stat_menu()
        self.draw_legend_menu()
        # reset current row
        self.cur_row = self.WINDOW_TOP_MARGIN

        # draw header elements
        for elem in self.HEADER_ELEMS:
            if elem['text'] == 'auction':
                if self.cur_auction:
                    self.center_text("Current auction: " +
                                     self.cur_auction.__str__(), elem['attr'])
                else:
                    self.center_text("Done!", elem['attr'])
                continue
            elif elem['text'] == 'bid':
                if self.cur_auction:
                    self.center_text(f"Highest bidder: {self.cur_auction.bidder} "
                                     f"({self.cur_auction.current_bid} / {self.cur_auction.current_bid_str})", elem['attr'])
                else:
                    self.center_text("-", elem['attr'])
                continue

            self.center_text(elem['text'], elem['attr'])

        # draw team table
        for i in range(len(self.teams)):
            attr = curses.color_pair(constants.COLOUR_SUCCESS_MSG) \
                if len(self.teams[i].chores) >= self.n_chores_per_team else 0
            self.center_text(self.teams[i].ui_row_string(), attr=attr)

        self.center_text(self.HR)

        # draw text boxes
        self.text_box_text("Place bid", "left", curses.A_UNDERLINE)
        self.text_box_text("Convert", "right", curses.A_UNDERLINE)
        self.bid_edit_win, self.bid_box = self.make_textbox(
            1, self.input_textbox_cols, self.cur_row + 2, curses.COLS // 2 - int(self.input_textbox_cols * 1.5))
        self.convert_edit_win, self.convert_box = self.make_textbox(
            1, self.input_textbox_cols, self.cur_row + 2, curses.COLS // 2 + self.input_textbox_cols // 2)

        # textboxes are thicc, so add plenty spacing
        self.msg_output_row = self.cur_row + 5
        self.log_textbox_row = self.cur_row + 7

        # draw output log textbox
        self.center_text('Output log', curses.A_UNDERLINE, self.log_textbox_row)
        self.log_win, self.log_textbox = self.make_textbox(
            self.log_textbox_row_limit, self.log_textbox_cols, self.log_textbox_row + 3,
            curses.COLS // 2 - self.log_textbox_cols // 2, insert_mode=False
        )

        # draw log messages in log textbox
        log_row = 0
        for msg in self.log_textbox_msgs:
            self.log_win.addstr(log_row, 0, msg.txt, msg.attr)
            log_row += 1

        # draw output message from action, if present
        if self.msg:
            self.center_text(self.msg.txt, attr=self.msg.attr, row=self.msg_output_row)

    def event_loop(self):
        """
        Main event loop of the tjanseauktion.

        We continually request keys from the user. If one is present we perform the corresponding
        action and re-draw the UI.
        """
        while True:
            action = self.window.getch()
            self.msg = None

            if action == ord('b'):
                self._bid_action()

            elif action == ord('c'):
                self._convert_action()

            elif action == ord('s'):
                self._sell_chore_action()

            elif action == ord('r'):
                self._reset_auction_action()

            elif action == ord('p'):
                self._revert_last_auction_action()

            self.log_last_message()
            self.state_logger.log_state(self.teams, self.auctions, self.completed_auctions, self.cur_auction)

            self.window.clear()
            self.draw_ui()
            # re-hide cursor in case we entered edit mode in previous action
            curses.curs_set(0)
            self.window.refresh()
            # log window needs to be refreshed AFTER main window, otherwise all text
            # is yeeted by black magic
            self.log_win.refresh()

    def _bid_action(self):
        """
        Bid action. Triggered by the 'b' key.

        Try performing a bid and return a corresponding message to UI.
        """
        # show cursor when entering edit mode
        curses.curs_set(1)
        msg = self.bid_box.edit()
        if not msg:
            # esc is pressed
            pass

        elif InputValidation.validate_bid_instant_win(msg):
            team_id = self.parse_instant_win_bid(msg)
            if team_id > len(self.teams):
                self.msg = Message(f"Error: team{team_id} does not exist",
                                   attr=curses.color_pair(constants.COLOUR_ERR_MSG))
            else:
                team = self.teams[team_id]
                if not team.has_free_win:
                    self.msg = Message(f"Error: team{team.id} has already used their instant win",
                                       attr=curses.color_pair(constants.COLOUR_ERR_MSG))
                else:
                    self.msg = self.cur_auction.instant_win(team)
                    self._prepare_next_auction()

        elif InputValidation.validate_bid_input(msg):
            team_id, bid = self.parse_bid(msg.strip())
            if team_id > len(self.teams):
                self.msg = Message(f"Error: team{team_id} does not exist",
                                   attr=curses.color_pair(constants.COLOUR_ERR_MSG))
            else:
                normalized_msg = ':'.join(x if x else '0' for x in msg.split()[1].split(':')).strip()
                self.msg = self.cur_auction.try_bid(bid, self.teams[team_id], normalized_msg,
                                                    self.cfg.auction_min_overbid_factor())

        elif InputValidation.validate_bid_freebie(msg):
            team_id = self.parse_freebie_bid(msg)
            if sum(1 for x in self.teams if not len(x.chores) == self.n_chores_per_team) > 1:
                self.msg = Message(f"Error: more than 1 team still needs chores - freebie can't be used yet",
                                   attr=curses.color_pair(constants.COLOUR_ERR_MSG))
            elif team_id > len(self.teams):
                self.msg = Message(f"Error: team{team_id} does not exist",
                                   attr=curses.color_pair(constants.COLOUR_ERR_MSG))
            else:
                self.msg = self.cur_auction.freebie(self.teams[team_id])
                self._prepare_next_auction()

        else:
            self.msg = Message(f"Error: input not valid ({msg.strip()}). Check command menu for syntax.",
                               attr=curses.color_pair(constants.COLOUR_ERR_MSG))
        self.bid_edit_win.clear()

    def _convert_action(self):
        """
        Currency conversion action. Triggered by the 'c' key.

        Try performing a conversion and return a corresponding message to UI.
        """
        # show cursor when entering edit mode
        curses.curs_set(1)
        msg = self.convert_box.edit()
        if not msg:
            # esc is pressed
            pass
        elif InputValidation.validate_convert_input(msg):
            value = self.parse_conversion(msg.strip())
            normalized_msg = ':'.join(x if x else '0' for x in msg.split(':')).strip()
            self.msg = Message(f"\"{normalized_msg}\" is {value} coins",
                               attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))
        else:
            self.msg = Message(f"Error: input not valid ({msg.strip()}). Check command menu for syntax.",
                               attr=curses.color_pair(constants.COLOUR_ERR_MSG))
        self.bid_edit_win.clear()

    def _sell_chore_action(self):
        """
        Sell chore action. Triggered by the 's' key.

        Sell the current auction to the current highest bidder and setup the next auction.
        """
        if self.cur_auction.bidder:
            self.msg = self.cur_auction.complete_auction()
            self._prepare_next_auction()
        else:
            self.msg = Message(f"Error: no bids have been made on auction",
                               attr=curses.color_pair(constants.COLOUR_ERR_MSG))

    def _reset_auction_action(self):
        """
        Reset auction action. Triggered by the 'r' key.

        Reset the state of the current auction
        """
        self.cur_auction.reset_bids()
        self.msg = Message('Reset current auction state',
                           attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))

    def _revert_last_auction_action(self):
        if len(self.completed_auctions) > 0:
            self.auctions.insert(0, self.cur_auction)
            self.cur_auction = self.completed_auctions.pop()
            # if bid is not present, instant win was used
            if self.cur_auction.current_bid == -1:
                self.cur_auction.bidder.has_free_win = True
            else:
                self.cur_auction.bidder.coins += self.cur_auction.current_bid
            self.cur_auction.bidder.chores.pop()
            self.cur_auction.reset_bids()
            self.msg = Message('Reverted last auction',
                               attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))
        else:
            self.msg = Message('Error: no auctions have been completed',
                               attr=curses.color_pair(constants.COLOUR_ERR_MSG))

    def _prepare_next_auction(self):
        if not self.auctions:
            # no more auctions remain
            OutputWriter.write_to_pdf(self.teams)
            self.msg = Message('All chores have been sold. MD saved to run dir.',
                               attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))
            self.completed_auctions.append(self.cur_auction)
            self.cur_auction = None
            return

        self.completed_auctions.append(self.cur_auction)
        self.cur_auction = self.auctions[0]
        del self.auctions[0]

    def center_text(self, txt: str, attr: int = 0, row: int = 0):
        """
        Draw :param txt with center alignment
        :param txt: string to print
        :param attr: any attributes of the text (e.g., bold font or colour)
        :param row: row index to print the text at
        """
        self.window.addstr(row if row else self.cur_row, curses.COLS // 2 - len(txt) // 2, txt, attr)
        self.cur_row += 1

    def left_margin_text(self, txt: str, row: int, attr: int = 0) -> int:
        """
        Draw :param txt with left alignment
        :param txt: string to print
        :param row: row index to print the text at
        :param attr: any attributes of the text (e.g., bold font or colour)
        """
        self.window.addstr(row, 0, txt, attr)
        row += 1
        return row

    def text_box_text(self, txt: str, alignment: str, attr: int = 0, row: int = 0):
        """
        Draw text above either of "Place bid" or "Convert" Textboxes, denoted by :param alignment.
        :param txt: string to print
        :param alignment: [ left | whatever for right, me code good ]
        :param attr: any attributes of the text (e.g., bold font or colour)
        :param row: row index to print the text at
        """
        col = curses.COLS // 2 - len(txt) // 2
        col = col - self.input_textbox_cols if alignment == 'left' else col + self.input_textbox_cols
        self.window.addstr(row if row else self.cur_row, col, txt, attr)

    def make_textbox(self, h: int, w: int, y: int, x: int, insert_mode: bool = True):
        """
        Generate a textbox with input dimensions and location
        """
        win = curses.newwin(h, w, y, x)
        box = Fextbox(win, insert_mode=insert_mode)
        rectangle(self.window, y-1, x-1, y+h, x+w)

        return win, box

    @staticmethod
    def parse_bid(bid: str) -> tuple:
        """
        Parse bid string input from bid Textbox. Doesn't include any validation, and should as such
        be called after its' corresponding InputValidation handler
        """
        rates = [constants.HIGH_VALUE, constants.MID_VALUE, constants.LOW_VALUE]
        team_id, bid_str = bid.split(' ')
        currency_bids = [int(x) if x else '' for x in bid_str.split(':')]
        bid_int = sum(cash * rate for cash, rate in zip(currency_bids, rates) if cash) or 0

        return int(team_id), bid_int

    @staticmethod
    def parse_instant_win_bid(bid: str) -> int:
        """
        Parse instant win bid string input from bid Textbox. Doesn't include any validation,
        and should as such be called after its' corresponding InputValidation handler
        """
        return int(bid.split()[0])

    @staticmethod
    def parse_freebie_bid(bid: str) -> int:
        """
        Parse freebie bid string input from bid Textbox. Doesn't include any validation,
        and should as such be called after its' corresponding InputValidation handler
        """
        return int(bid.split()[0])

    @staticmethod
    def parse_conversion(conversion: str) -> int:
        """
        Parse conversion string input from bid Textbox. Doesn't include any validation, and should
        as such be called after its' corresponding InputValidation handler
        """
        rates = [constants.HIGH_VALUE, constants.MID_VALUE, constants.LOW_VALUE]
        conversions = [int(x) if x else '' for x in conversion.split(':')]
        value = sum(cash * rate for cash, rate in zip(conversions, rates) if cash) or 0

        return value

    def log_last_message(self):
        if len(self.log_textbox_msgs) >= 10:
            _ = self.log_textbox_msgs.pop()

        if self.msg:
            self.log_textbox_msgs.insert(0, self.msg)
            self.msg_logger.log_msg(self.msg)

    def draw_help_text(self):
        """
        Draw help text in UI and setup initial statistics text row
        """
        cur_row = self.left_margin_text('Command menu', 1, curses.A_UNDERLINE)
        cur_row = self.left_margin_text(self.HR, cur_row)

        for cmd in self.CMD_MENU:
            if 'cmd' in cmd.keys():
                cur_row = self.left_margin_text(f'{cmd["cmd"]} -> {cmd["help"]}', cur_row)
            else:
                cur_row = self.left_margin_text(f'\t{cmd["help"]}', cur_row)

        self.stat_menu_row = cur_row + 3

    def draw_stat_menu(self):
        """
        Draw statistics menu
        """
        cur_row = self.stat_menu_row

        cur_row = self.left_margin_text('Statistics', cur_row, curses.A_UNDERLINE)
        cur_row = self.left_margin_text(self.HR, cur_row)

        # +1 because we delete after current auction is selected
        auctions_left = len(self.auctions) + (1 if self.cur_auction else 0)
        auctions_done = len(self.completed_auctions)
        secrets_left = sum(1 for x in self.auctions if x.is_secret)
        free_chores_left = sum(1 for x in self.auctions if x.chore.desc == 'Fritjans')
        cur_row = self.left_margin_text(common.string_with_spacing(f'Total auctions:', spacing=30) + f'{auctions_left + auctions_done}', cur_row)
        cur_row = self.left_margin_text(common.string_with_spacing(f'Auctions left:', spacing=30) + f'{auctions_left}', cur_row)
        cur_row = self.left_margin_text(common.string_with_spacing(f'Auctions done:', spacing=30) + f'{auctions_done}', cur_row)
        cur_row = self.left_margin_text(common.string_with_spacing(f'Secrets left:', spacing=30) + f'{secrets_left}', cur_row)
        cur_row = self.left_margin_text(common.string_with_spacing(f'Free chores left:', spacing=30) + f'{free_chores_left}', cur_row)
        cur_row = self.left_margin_text(common.string_with_spacing(f'Chores per team:', spacing=30) + f'{self.n_chores_per_team}', cur_row)

        self.legend_menu_row = cur_row + 3

    def draw_legend_menu(self):
        cur_row = self.legend_menu_row

        cur_row = self.left_margin_text('Legend', cur_row, curses.A_UNDERLINE)
        cur_row = self.left_margin_text(self.HR, cur_row)

        high = f'{common.string_with_spacing("High:", spacing=15)}' \
               f'{common.string_with_spacing(self.cfg.currency_high_name())}{constants.HIGH_VALUE}'
        cur_row = self.left_margin_text(high, cur_row)
        mid = f'{common.string_with_spacing("Mid:", spacing=15)}' \
              f'{common.string_with_spacing(self.cfg.currency_mid_name())}{constants.MID_VALUE}'
        cur_row = self.left_margin_text(mid, cur_row)
        low = f'{common.string_with_spacing("Low:", spacing=15)}' \
              f'{common.string_with_spacing(self.cfg.currency_low_name())}{constants.LOW_VALUE}'
        cur_row = self.left_margin_text(low, cur_row)
        instant_win = f'{common.string_with_spacing("Instant win:", spacing=15)}' \
                      f'{common.string_with_spacing(self.cfg.currency_instant_win_name())}'
        cur_row = self.left_margin_text(instant_win, cur_row)