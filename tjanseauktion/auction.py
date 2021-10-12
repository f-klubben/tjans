from . import constants
from .chore import Chore
from .team import Team
from .message import Message

import random
import curses
import math
from typing import Optional


class Auction:

    def __init__(self, chore: Chore):
        self.chore = chore

        self.current_bid = 0
        self.current_bid_str = ''
        self.bidder = None  # type: Optional[Team]
        self.is_completed = False
        self.is_secret = False

    def __str__(self) -> str:
        return f'[SECRET] - {self.chore.__str__()}' if self.is_secret else self.chore.__str__()

    def __eq__(self, other):
        if not other:
            return False
        return self.chore == self.chore

    def is_bid_valid(self, bid: int) -> bool:
        """
        Ensure bid is valid
        :param bid: bid being placed
        """
        if bid <= self.current_bid:
            return False
        return True

    def is_bidder_valid(self, bidder: Team) -> bool:
        """
        Ensure bidder is valid
        :param bidder: team placing the bid
        """
        if bidder == self.bidder:
            return False
        return True

    def try_bid(self, bid: int, bidder: Team, bid_str: str) -> Message:
        """
        Try placing bid
        :param bid: bid being placed
        :param bidder: team placing the bid
        :param bid_str: bid string queried in the ui
        :return: Message object containing resulting success/error message
        """
        if not self.is_bid_valid(bid):
            return Message(f'Error: bid is too low ({bid} / {self.current_bid})',
                           attr=curses.color_pair(constants.COLOUR_ERR_MSG))

        if not self.is_bidder_valid(bidder):
            return Message(f'Error: bidder already has the lead',
                           attr=curses.color_pair(constants.COLOUR_ERR_MSG))

        if not bidder.can_afford(bid):
            return Message(f"Error: bidder can't afford {bidder.coins}/{bid}",
                           attr=curses.color_pair(constants.COLOUR_ERR_MSG))

        self.current_bid = bid
        self.current_bid_str = bid_str
        self.bidder = bidder

        return Message(f'team{bidder.id} bid {bid} coins ({bid_str})',
                       attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))

    def instant_win(self, buyer: Team) -> Message:
        """
        Try winning auction with instant win
        :param buyer: team using instant win
        """
        self.current_bid = -1
        self.current_bid_str = f'{buyer.id} win'
        self.bidder = buyer
        self.is_completed = True
        buyer.instant_win(self.chore)

        return Message(f"team{buyer.id} used instant win, it's super effective!",
                       attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))

    def complete_auction(self) -> Message:
        """
        Bidder buys chore and state of auction is set to complete
        """
        self.bidder.buy(self.chore, self.current_bid)
        self.is_completed = True

        return Message(f'Chore {self.chore.desc} sold to team{self.bidder.id}',
                       attr=curses.color_pair(constants.COLOUR_SUCCESS_MSG))

    @classmethod
    def create_auctions(cls, chores: list, n_secrets: int, n_teams: int) -> list:
        """
        Generate list of auctions from chore list.
        :param chores: list of chores as defined by ./data/chores.json
        :param n_secrets: amount of secret auctions to generate, as defined by ./cfg.ini
        :param n_teams: amount of teams generated, as defined by ./cfg.ini
        """
        auctions = [Auction(chore) for chore in chores]
        random.seed()

        # set secrets
        for i in range(n_secrets):
            selection = random.choice(auctions)

            while selection.is_secret:
                selection = random.choice(auctions)

            selection.is_secret = True

        """
        the amount of free chores is the amount of chores remaining given x chores per team
        that is, with 12 teams and 45 chores, each team needs 4 chores and 3 chores will be free chores
        
        with the current chore list we have 49 chores - this would equal 11 free chores (too much)
        with the original tjanseauktion list, we had 48 chores - this would equal 0 free chores
        how did we ever have any free chores?
        """
        chores_per_team = math.ceil(len(chores) / n_teams)
        n_free_chores = (chores_per_team * n_teams) % len(chores)

        for i in range(n_free_chores):
            a = Auction(Chore('Fritjans', '', ''))
            a.is_secret = True
            auctions.append(a)

        # shuffle auctions and make sure we start with monday chores
        random.shuffle(auctions)
        auctions = [
            *[x for x in auctions if x.chore.day == 'Mandag'],
            *[x for x in auctions if x.chore.day != 'Mandag']
        ]

        return auctions

    def reset_bids(self) -> None:
        """
        Reset auction to initial state
        """
        self.bidder = None
        self.current_bid = 0
        self.current_bid_str = ''

    def to_json(self):
        return {
            'chore': self.chore.to_json(),
            'current_bid': self.current_bid,
            'current_bid_str': self.current_bid_str,
            'bidder': self.bidder.to_json() if self.bidder else None,
            'is_completed': self.is_completed,
            'is_secret': self.is_secret
        }

    @classmethod
    def from_json(cls, row: dict):
        a = Auction(Chore.from_json(row['chore']))
        a.current_bid = row['current_bid']
        a.current_bid_str = row['current_bid_str']
        a.bidder = Team.from_json(row['bidder']) if row['bidder'] else None
        a.is_completed = row['is_completed']
        a.is_secret = row['is_secret']

        return a