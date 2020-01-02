import unittest

from src import utils


class TestUnits(unittest.TestCase):
    def test_ba2int(self):
        arg = (False, True, False, True, False)
        actual = utils.ba2int(arg)
        expected = 10
        self.assertEqual(expected, actual)

    def test_int2bastr(self):
        arg = 10
        actual = utils.int2bastr(arg, 5)
        expected = '01010'
        self.assertEqual(expected, actual)

    def test_bastr2ba(self):
        arg = '01010'
        actual = utils.bastr2ba(arg)
        expected = (False, True, False, True, False)
        self.assertEqual(expected, actual)

    def test_int2ba(self):
        arg = 10
        actual = utils.int2ba(arg, 5)
        expected = (False, True, False, True, False)
        self.assertEqual(expected, actual)
