from tjanseauktion.config import Config

import unittest


class TestConfig(unittest.TestCase):

    def setUp(self) -> None:
        Config.FILE_NAME = 'tests/fixtures/test_cfg.ini'
        self.cfg = Config()

    def test_cfg_sections(self):
        sections = ['auction', 'currency']
        self.assertListEqual(self.cfg.cfg.sections(), sections)

    def test_auction_n_teams(self):
        self.assertEqual(self.cfg.auction_n_teams(), 500)

    def test_auction_n_secrets(self):
        self.assertEqual(self.cfg.auction_n_secrets(), 1000)

    def test_currency_high_name(self):
        self.assertEqual(self.cfg.currency_high_name(), "big doinks")

    def test_currency_mid_name(self):
        self.assertEqual(self.cfg.currency_mid_name(), "medium doinks")

    def test_currency_low_name(self):
        self.assertEqual(self.cfg.currency_low_name(), "small doinks")

    def test_currency_instant_win_name(self):
        self.assertEqual(self.cfg.currency_instant_win_name(), "absolute doinks")