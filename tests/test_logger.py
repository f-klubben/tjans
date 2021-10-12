from tjanseauktion import logger
from tjanseauktion.logger import MessageLogger, StateLogger
from tjanseauktion.message import Message
from tjanseauktion.auction import Auction
from tjanseauktion.chore import Chore
from tjanseauktion.team import Team

import os
import unittest
import json


class TestMessageLogger(unittest.TestCase):

    def setUp(self) -> None:
        logger.LOG_DIR = 'tests/fixtures'
        logger.TIMESTAMP = '4-20-1969'

        self.logger = MessageLogger()

    def tearDown(self) -> None:
        if os.path.isfile(self.logger.path):
            os.remove(self.logger.path)

    def test_init(self):
        self.assertEqual(self.logger.path, "tests/fixtures/message-log-4-20-1969.txt")
        self.assertTrue(os.path.isfile(self.logger.path))

    def test_log_msg(self):
        msg = Message("some informative log message")

        self.logger.log_msg(msg)

        with open(self.logger.path, 'r') as f:
            self.assertEqual(f.read(), msg.txt + '\n')


class TestStateLogger(unittest.TestCase):

    def setUp(self) -> None:
        logger.LOG_DIR = 'tests/fixtures'
        logger.TIMESTAMP = '4-20-1969'

        self.logger = StateLogger()

        self.teams = [Team(0), Team(1), Team(2)]
        chores = Chore.load_chores(path="tests/fixtures/test_chores.json")
        self.auctions = [Auction(c) for c in chores]
        self.cur_auction = self.auctions[0]

        self.state_json = {
            'teams': [x.to_json() for x in self.teams],
            'auctions': [x.to_json() for x in self.auctions],
            'completed_auctions': [],
            'cur_auction': self.cur_auction.to_json()
        }

    def tearDown(self) -> None:
        if os.path.isfile(self.logger.path):
            os.remove(self.logger.path)

    def test_init(self):
        self.assertEqual(self.logger.path, "tests/fixtures/state-log-4-20-1969.json")
        self.assertTrue(os.path.isfile(self.logger.path))

        default = {
            'teams': [],
            'auctions': [],
            'completed_auctions': [],
            'cur_auction': None
        }

        with open(self.logger.path, 'r') as f:
            data = json.loads(f.read())

        self.assertDictEqual(data, default)

    def test_log_state(self):
        self.logger.log_state(self.teams, self.auctions, [], self.cur_auction)

        with open(self.logger.path, 'r') as f:
            data = json.loads(f.read())

        self.assertDictEqual(data, self.state_json)

    def test_load_state(self):
        self.logger.log_state(self.teams, self.auctions, [], self.cur_auction)

        teams, auctions, completed_auctions, cur_auction = self.logger.load_state()

        self.assertListEqual(teams, self.teams)
        self.assertListEqual(auctions, self.auctions)
        self.assertListEqual(completed_auctions, [])
        self.assertEqual(cur_auction, self.cur_auction)

    def test_is_state_log_present(self):
        self.assertFalse(self.logger.is_state_log_present())
        self.logger.log_state(self.teams, self.auctions, [], self.cur_auction)
        self.assertTrue(self.logger.is_state_log_present())
        self.logger.log_state(self.teams, self.auctions, [self.cur_auction], self.cur_auction)
        self.assertTrue(self.logger.is_state_log_present())