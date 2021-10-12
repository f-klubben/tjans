from tjanseauktion import common

import unittest


class TestCommon(unittest.TestCase):

    def test_string_with_spacing(self):
        s = common.string_with_spacing("yeet", 20)
        self.assertEqual(len(s), 20)

        s = common.string_with_spacing("yote", 30)
        self.assertEqual(len(s), 30)

        s = common.string_with_spacing("yat", 15, offset=3)
        self.assertEqual(len(s), 18)