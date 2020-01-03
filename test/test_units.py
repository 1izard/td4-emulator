from numpy.testing import assert_array_equal
import numpy as np
from typing import Tuple, Callable
from nptyping import Array
import unittest

from src import units, utils

gen_all_bool_patterns = utils.gen_all_bool_patterns
all_assert_equal = utils.all_assert_equal


class TestUnits(unittest.TestCase):
    def get_actuals(self, fn: Callable[[bool], bool], pattern_length: int) -> Tuple[bool]:
        args = gen_all_bool_patterns(pattern_length)
        return np.array(tuple(fn(*arg) for arg in args))

    def test_NOT(self):
        actuals = self.get_actuals(units.NOT, 1)
        expecteds = np.array((True, False))
        assert_array_equal(expecteds, actuals)

    def test_AND(self):
        actuals = self.get_actuals(units.AND, 2)
        expecteds = np.array((False, False, False, True))
        assert_array_equal(expecteds, actuals)

    def test_OR(self):
        actuals = self.get_actuals(units.OR, 2)
        expecteds = np.array((False, True, True, True))
        assert_array_equal(expecteds, actuals)

    def test_NAND(self):
        actuals = self.get_actuals(units.NAND, 2)
        expecteds = np.array((True, True, True, False))
        all_assert_equal(self, expecteds, actuals)
        assert_array_equal(expecteds, actuals)

    def test_NOR(self):
        actuals = self.get_actuals(units.NOR, 2)
        expecteds = np.array((True, False, False, False))
        assert_array_equal(expecteds, actuals)

    def test_XOR(self):
        actuals = self.get_actuals(units.XOR, 2)
        expecteds = np.array((False, True, True, False))
        assert_array_equal(expecteds, actuals)

    def test_HA(self):
        actuals = self.get_actuals(units.HA, 2)
        expecteds = np.array(((0, 0), (0, 1), (0, 1), (1, 0)))
        assert_array_equal(expecteds, actuals)

    def test_FA(self):
        actuals = np.array(self.get_actuals(units.FA, 3))
        expecteds = np.array(((0, 0), (0, 1), (0, 1), (1, 0), (0, 1), (1, 0), (1, 0), (1, 1)))
        assert_array_equal(expecteds, actuals)

    def test_ALU(self):
        patterns = gen_all_bool_patterns(9)
        args = tuple((p[0], np.array(p[1:5]), np.array(p[5:])) for p in patterns)
        actuals = np.array(tuple(units.ALU(*arg) for arg in args))

        def _get_expected(bit_c: bool, bit_arr_a: Array[bool, 1, 4], bit_arr_b: Array[bool, 1, 4])\
                -> Array[bool, 1, 5]:
            # reverse bit_arr because LSB is arr_a[0] and MSB is arr_a[-1] in ALU
            bit_arr_a = bit_arr_a[::-1]
            bit_arr_b = bit_arr_b[::-1]
            a_i = utils.ba2int(bit_arr_a)
            b_i = utils.ba2int(bit_arr_b)
            sum_i = a_i + b_i + int(bit_c)
            sum_bit_arr = utils.int2ba(sum_i, 5)
            # reverse bit_arr because LSB is arr_a[0] and MSB is arr_a[-1] in ALU
            return np.array((sum_bit_arr[0], *sum_bit_arr[1:][::-1]))

        expected = np.array(tuple(_get_expected(*arg) for arg in args))
        assert_array_equal(expected, actuals)

    def test_AR(self):
        patterns = gen_all_bool_patterns(4)
        # reverse bit_arr because LSB is a and MSB is d in AR.
        # (g1, g2) is fixed with (0, 0)
        args = (p[::-1] + (0, 0) for p in patterns)
        actuals = np.array(tuple(units.AR(*arg) for arg in args))
        e = [[False for _ in range(16)] for _ in range(16)]
        for i in range(16):
            e[i][i] = True
        expected = np.array(e)
        assert_array_equal(expected, actuals)


if __name__ == '_main__':
    unittest.main()
