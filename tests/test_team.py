from tjanseauktion.team import Team
from tjanseauktion.chore import Chore

import unittest


class TestTeam(unittest.TestCase):

    def setUp(self) -> None:
        self.team = Team(0)

    def test_str(self):
        self.assertEqual(self.team.__str__(), "team0")

    def test_eq(self):
        team_eq = Team(0)
        team_neq = Team(1)

        self.assertTrue(self.team == team_eq)
        self.assertFalse(self.team == team_neq)

    def test_coin_string(self):
        s = self.team.coin_string()
        self.assertEqual(s, "10.2.12 | 5000 | ★")

        self.team.has_free_win = False
        s = self.team.coin_string()
        self.assertEqual(s, "10.2.12 | 5000 | ☠")

    def test_ui_row_string(self):
        s = self.team.ui_row_string()

        self.assertIn("Chores: 0", s)
        self.assertIn("ID: 0", s)
        self.assertIn("team0", s)
        self.assertIn("10.2.12 | 5000 | ★", s)

    def test_can_afford(self):
        self.assertTrue(self.team.can_afford(2000))
        self.assertTrue(self.team.can_afford(5000))
        self.assertFalse(self.team.can_afford(5001))

    def test_buy(self):
        chore = Chore("some chore", "today", "now")
        self.assertFalse(self.team.buy(chore, 5001))

        self.team.buy(chore, 2000)
        self.assertEqual(self.team.coins, 3000)
        self.assertIn(chore, self.team.chores)

    def test_instant_win(self):
        chore = Chore("some chore", "today", "now")
        self.team.instant_win(chore)
        self.assertIn(chore, self.team.chores)
        self.assertFalse(self.team.has_free_win)

    def test_add_chore(self):
        chore = Chore("some chore", "today", "now")
        self.team.add_chore(chore)
        self.assertIn(chore, self.team.chores)

    def test_to_json(self):
        expected = {
            'coins': 5000,
            'chores': [],
            'id': 0,
            'has_free_win': True
        }

        j = self.team.to_json()

        self.assertDictEqual(j, expected)

    def test_from_json(self):
        j = {
            'coins': 5000,
            'chores': [],
            'id': 0,
            'has_free_win': True
        }

        t = Team.from_json(j)
        self.assertEqual(t.coins, 5000)
        self.assertListEqual(t.chores, [])
        self.assertEqual(t.id, 0)
        self.assertTrue(t.has_free_win)