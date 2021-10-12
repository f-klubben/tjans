from . import constants
from . import common
from .chore import Chore

import math
from typing import List


class Team:
    COIN_STR_LEN = 0

    def __init__(self, _id: int):
        self.coins = constants.START_COINS
        self.chores = []  # type: List[Chore]
        self.id = _id
        self.has_free_win = True

        # to ensure pretty UI format, we set and use the initial length of the coin strings
        # and use it as offset for the team table rows
        if not self.COIN_STR_LEN:
            self.COIN_STR_LEN = len(self.coin_string())

    def __str__(self):
        return f'team{self.id}'

    def __eq__(self, other):
        """
        Override == operator for Team objects such that we compare by team ID
        """
        if not other:
            return False
        return self.id == other.id

    def coin_string(self) -> str:
        """
        Generate coin string on the format "high.mid.low"
        """
        high = math.floor(self.coins / constants.HIGH_VALUE)
        mid = math.floor(self.coins % constants.HIGH_VALUE / constants.MID_VALUE)
        low = self.coins % constants.HIGH_VALUE % constants.MID_VALUE
        insta_win = '★' if self.has_free_win else '☠'

        return f'{high}.{mid}.{low} | {self.coins} | {insta_win}'

    def ui_row_string(self) -> str:
        """
        Construct string for a table row in the UI
        """
        chore_str = f'Chores: {len(self.chores)}'
        id_str = f'ID: {self.id}'
        name_str = f'team{self.id}'
        coin_str = self.coin_string()

        return f'{common.string_with_spacing(chore_str)}{common.string_with_spacing(id_str)}' \
               f'{common.string_with_spacing(name_str, offset=self.COIN_STR_LEN - len(coin_str))}{coin_str}'

    def can_afford(self, price: int) -> bool:
        """
        Check if team can afford a purchase given a price
        """
        return self.coins >= price

    def buy(self, chore: Chore, price: int) -> bool:
        """
        Purchase a chore
        """
        if not self.can_afford(price):
            return False

        self.coins -= price
        self.add_chore(chore)

    def instant_win(self, chore: Chore):
        """
        Use instant win to buy chore
        """
        self.has_free_win = False
        self.add_chore(chore)

    def add_chore(self, chore: Chore):
        """
        Add chore to the teams list of chores
        """
        self.chores.append(chore)

    def to_json(self):
        return {
            'coins': self.coins,
            'chores': [x.to_json() for x in self.chores],
            'id': self.id,
            'has_free_win': self.has_free_win
        }

    @classmethod
    def from_json(cls, row: dict):
        t = Team(row['id'])
        t.coins = row['coins']
        t.chores = [Chore.from_json(r) for r in row['chores']]
        t.has_free_win = row['has_free_win']

        return t