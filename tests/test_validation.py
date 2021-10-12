from tjanseauktion.validation import InputValidation

import unittest


class TestInputValidation(unittest.TestCase):

    def test_validate_bid_input(self):
        self.assertTrue(InputValidation.validate_bid_input("1 ::"))
        self.assertTrue(InputValidation.validate_bid_input("2 2::"))
        self.assertTrue(InputValidation.validate_bid_input("3 :4:"))
        self.assertTrue(InputValidation.validate_bid_input("7 ::4"))
        self.assertTrue(InputValidation.validate_bid_input("9 1::1"))
        self.assertTrue(InputValidation.validate_bid_input("69 4:20:"))
        self.assertTrue(InputValidation.validate_bid_input("2 :2:2"))
        self.assertTrue(InputValidation.validate_bid_input("4 1:1:1  "))

        self.assertFalse(InputValidation.validate_bid_input("::"))
        self.assertFalse(InputValidation.validate_bid_input("2 2"))
        self.assertFalse(InputValidation.validate_bid_input("3 2:"))
        self.assertFalse(InputValidation.validate_bid_input("f ::2"))

    def test_validate_bid_instant_win(self):
        self.assertTrue(InputValidation.validate_bid_instant_win("4 win"))
        self.assertTrue(InputValidation.validate_bid_instant_win("9 win   "))

        self.assertFalse(InputValidation.validate_bid_instant_win("f win"))
        self.assertFalse(InputValidation.validate_bid_instant_win("1 iwn"))

    def test_validate_convert_input(self):
        self.assertTrue(InputValidation.validate_convert_input("::"))
        self.assertTrue(InputValidation.validate_convert_input("2::"))
        self.assertTrue(InputValidation.validate_convert_input(":4:"))
        self.assertTrue(InputValidation.validate_convert_input("::4"))
        self.assertTrue(InputValidation.validate_convert_input("1::1"))
        self.assertTrue(InputValidation.validate_convert_input("4:20:"))
        self.assertTrue(InputValidation.validate_convert_input(":2:2"))
        self.assertTrue(InputValidation.validate_convert_input("1:1:1  "))