from tjanseauktion.ui import UI

import unittest


class TestUI(unittest.TestCase):

    def test_parse_bid(self):
        team_id, bid = UI.parse_bid("2 ,,")
        self.assertEqual(team_id, 2)
        self.assertEqual(bid, 0)

        team_id, bid = UI.parse_bid("10 2,,14")
        self.assertEqual(team_id, 10)
        self.assertEqual(bid, 1000)

        _, bid = UI.parse_bid("10 ,1,500")
        self.assertEqual(bid, 529)

    def test_parse_instant_win_bid(self):
        team_id = UI.parse_instant_win_bid("5 win")
        self.assertEqual(team_id, 5)

        team_id = UI.parse_instant_win_bid("0 win")
        self.assertEqual(team_id, 0)

        team_id = UI.parse_instant_win_bid("11 win")
        self.assertEqual(team_id, 11)

    def test_parse_conversion(self):
        value = UI.parse_conversion(",,")
        self.assertEqual(value, 0)

        value = UI.parse_conversion("2,2,14")
        self.assertEqual(value, 1058)

        value = UI.parse_conversion(",10,10")
        self.assertEqual(value, 300)