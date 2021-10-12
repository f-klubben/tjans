from tjanseauktion import constants
from tjanseauktion.auction import Auction
from tjanseauktion.chore import Chore
from tjanseauktion.team import Team

import unittest
import curses


class TestAuction(unittest.TestCase):

    def setUp(self) -> None:
        curses.initscr()
        if curses.has_colors():
            curses.start_color()
        curses.init_pair(constants.COLOUR_ERR_MSG, curses.COLOR_RED, 0)
        curses.init_pair(constants.COLOUR_SUCCESS_MSG, curses.COLOR_GREEN, 0)

        self.auction = Auction(
            Chore("some chore", "yesterday", "25:00")
        )

    def tearDown(self) -> None:
        curses.endwin()
        curses.reset_shell_mode()

    def test_str(self):
        self.assertEqual(self.auction.__str__(), "some chore - yesterday at 25:00")
        self.auction.is_secret = True
        self.assertEqual(self.auction.__str__(), "[SECRET] - some chore - yesterday at 25:00")

    def test_is_bid_valid(self):
        self.assertTrue(self.auction.is_bid_valid(10))
        self.auction.current_bid = 500
        self.assertFalse(self.auction.is_bid_valid(400))

    def test_is_bidder_valid(self):
        bidder0 = Team(0)
        bidder1 = Team(1)

        self.assertTrue(self.auction.is_bidder_valid(bidder0))
        self.auction.bidder = bidder0
        self.assertFalse(self.auction.is_bidder_valid(bidder0))
        self.assertTrue(self.auction.is_bidder_valid(bidder1))

    def test_try_bid_too_low(self):
        bidder = Team(0)
        self.auction.current_bid = 2000
        msg = self.auction.try_bid(500, bidder, '0 1::7')
        self.assertEqual(msg.txt, "Error: bid is too low (500 / 2000) (0 1::7)")
        self.assertEqual(msg.attr, curses.color_pair(constants.COLOUR_ERR_MSG))

    def test_try_bid_bidder_has_lead(self):
        bidder = Team(0)
        self.auction.bidder = bidder
        msg = self.auction.try_bid(500, bidder, '')
        self.assertEqual(msg.txt, "Error: bidder already has the lead (team0)")
        self.assertEqual(msg.attr, curses.color_pair(constants.COLOUR_ERR_MSG))

    def test_try_bid_cant_afford(self):
        bidder = Team(0)
        bidder.coins = 200
        msg = self.auction.try_bid(500, bidder, '0 1::7')
        self.assertEqual(msg.txt, "Error: bidder can't afford (200 / 500) (0 1::7)")
        self.assertEqual(msg.attr, curses.color_pair(constants.COLOUR_ERR_MSG))

    def test_try_bid_success(self):
        bidder = Team(0)
        bid_str = '1:0:0'
        bid = 493
        msg = self.auction.try_bid(bid, bidder, bid_str)
        self.assertEqual(msg.txt, "team0 bid 493 coins (1:0:0)")
        self.assertEqual(self.auction.current_bid, bid)
        self.assertEqual(self.auction.current_bid_str, bid_str)
        self.assertEqual(self.auction.bidder, bidder)
        self.assertEqual(msg.attr, curses.color_pair(constants.COLOUR_SUCCESS_MSG))

    def test_instant_win(self):
        buyer = Team(0)
        msg = self.auction.instant_win(buyer)
        self.assertEqual(msg.txt, "team0 used instant win, it's super effective!")
        self.assertEqual(msg.attr, curses.color_pair(constants.COLOUR_SUCCESS_MSG))
        self.assertEqual(self.auction.current_bid, -1)
        self.assertEqual(self.auction.current_bid_str, "0 win")
        self.assertEqual(self.auction.bidder, buyer)
        self.assertTrue(self.auction.is_completed)

    def test_complete_auction(self):
        bidder = Team(0)
        self.auction.bidder = bidder
        self.auction.current_bid = 500
        msg = self.auction.complete_auction()
        self.assertEqual(msg.txt, "Chore some chore sold to team0")
        self.assertEqual(msg.attr, curses.color_pair(constants.COLOUR_SUCCESS_MSG))
        self.assertTrue(self.auction.is_completed)

    def test_create_auctions(self):
        chores = [
            Chore("yeet the rich", "now", "now"),
            Chore("attend gulag", "Mandag", "7:00"),
            Chore("abolish capitalist society", "asap", "*")
        ]
        n_secrets = 2
        auctions = Auction.create_auctions(chores, n_secrets, 1)
        self.assertEqual(len(auctions), len(chores))
        self.assertEqual(sum(1 for x in auctions if x.is_secret), n_secrets)
        # monday chore should be first
        self.assertEqual(auctions[0].chore, chores[1])

    def test_reset_bids(self):
        team = Team(0)
        self.auction.bidder = team
        self.auction.current_bid = 500
        self.auction.current_bid_str = 'yeet'

        self.auction.reset_bids()
        self.assertIsNone(self.auction.bidder)
        self.assertEqual(self.auction.current_bid, 0)
        self.assertEqual(self.auction.current_bid_str, '')

    def test_to_json(self):
        j = self.auction.to_json()
        expected = {
            'chore': {
                'desc': "some chore",
                'day': "yesterday",
                'time': "25:00"
            },
            'current_bid': 0,
            'current_bid_str': "",
            'bidder': None,
            'is_completed': False,
            'is_secret': False
        }

        self.assertDictEqual(j, expected)

    def test_from_json(self):
        j = {
            'chore': {
                'desc': "some chore",
                'day': "yesterday",
                'time': "25:00"
            },
            'current_bid': 0,
            'current_bid_str': "",
            'bidder': None,
            'is_completed': False,
            'is_secret': False
        }

        auction = Auction.from_json(j)
        self.assertIsNotNone(auction.chore)
        self.assertEqual(auction.current_bid, 0)
        self.assertEqual(auction.current_bid_str, "")
        self.assertIsNone(auction.bidder)
        self.assertFalse(auction.is_completed)
        self.assertFalse(auction.is_secret)