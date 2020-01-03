import unittest
from numpy.testing import assert_array_equal
import numpy as np

from src import utils


class TestUnits(unittest.TestCase):
    def test_ba2int(self):
        arg = np.array((False, True, False, True, False))
        actual = utils.ba2int(arg)
        expected = 10
        assert_array_equal(expected, actual)

    def test_int2bastr(self):
        arg = 10
        actual = utils.int2bastr(arg, 5)
        expected = '01010'
        assert_array_equal(expected, actual)

    def test_bastr2ba(self):
        arg = '01010'
        actual = utils.bastr2ba(arg)
        expected = np.array((False, True, False, True, False))
        assert_array_equal(expected, actual)

    def test_int2ba(self):
        arg = 10
        actual = utils.int2ba(arg, 5)
        expected = np.array((False, True, False, True, False))
        assert_array_equal(expected, actual)
