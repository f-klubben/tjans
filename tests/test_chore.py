from tjanseauktion.chore import Chore

import unittest


class TestChore(unittest.TestCase):

    def setUp(self) -> None:
        self.chore = Chore("some chore", "yesterday", "25:00")

    def test_str(self):
        self.assertEqual(self.chore.__str__(), "some chore - yesterday at 25:00")

    def test_load_chores(self):
        chores = Chore.load_chores(path='tests/fixtures/test_chores.json')

        self.assertEqual(len(chores), 3)
        self.assertIsNotNone(chores[0].desc)
        self.assertIsNotNone(chores[0].day)
        self.assertIsNotNone(chores[0].time)

    def test_from_json(self):
        j = {
            'desc': "yeet the rich",
            'day': "today",
            'time': "now"
        }

        chore = Chore.from_json(j)
        self.assertEqual(chore.desc, j['desc'])
        self.assertEqual(chore.day, j['day'])
        self.assertEqual(chore.time, j['time'])

    def test_to_json(self):
        expected = {
            'desc': "some chore",
            'day': "yesterday",
            'time': "25:00"
        }
        j = self.chore.to_json()
        self.assertDictEqual(j, expected)
