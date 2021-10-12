from tjanseauktion.message import Message

import unittest


class TestMessage(unittest.TestCase):

    def test_eq(self):
        msg0 = Message("equal")
        msg1 = Message("equal")
        msg2 = Message("not equal")

        self.assertTrue(msg0 == msg1)
        self.assertFalse(msg0 == msg2)