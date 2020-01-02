from typing import Tuple, Callable
import unittest

from src import units, utils

gen_all_bool_patterns = utils.gen_all_bool_patterns
all_assert_equal = utils.all_assert_equal


class TestUnits(unittest.TestCase):
    def get_actuals(self, fn: Callable[[bool], bool], pattern_length: int) -> Tuple[bool]:
        args = gen_all_bool_patterns(pattern_length)
        return tuple(fn(*arg) for arg in args)

    def test_NOT(self):
        actuals = self.get_actuals(units.NOT, 1)
        expecteds = (True, False)
        all_assert_equal(self, expecteds, actuals)

    def test_AND(self):
        actuals = self.get_actuals(units.AND, 2)
        expecteds = (False, False, False, True)
        all_assert_equal(self, expecteds, actuals)

    def test_OR(self):
        actuals = self.get_actuals(units.OR, 2)
        expecteds = (False, True, True, True)
        all_assert_equal(self, expecteds, actuals)

    def test_NAND(self):
        actuals = self.get_actuals(units.NAND, 2)
        expecteds = (True, True, True, False)
        all_assert_equal(self, expecteds, actuals)

    def test_NOR(self):
        actuals = self.get_actuals(units.NOR, 2)
        expecteds = (True, False, False, False)
        all_assert_equal(self, expecteds, actuals)

    def test_XOR(self):
        actuals = self.get_actuals(units.XOR, 2)
        expecteds = (False, True, True, False)
        all_assert_equal(self, expecteds, actuals)

    def test_HA(self):
        actuals = self.get_actuals(units.HA, 2)
        expecteds = ((0, 0), (0, 1), (0, 1), (1, 0))
        all_assert_equal(self, expecteds, actuals)

    def test_FA(self):
        actuals = self.get_actuals(units.FA, 3)
        expecteds = ((0, 0), (0, 1), (0, 1), (1, 0), (0, 1), (1, 0), (1, 0), (1, 1))
        all_assert_equal(self, expecteds, actuals)

    def test_ALU(self):
        patterns = gen_all_bool_patterns(9)
        args = tuple((p[0], p[1:5], p[5:]) for p in patterns)
        actuals = tuple(units.ALU(*arg) for arg in args)

        def _get_expected(bit_c: bool, bit_arr_a: Tuple[bool], bit_arr_b: Tuple[bool])\
                -> Tuple[bool, Tuple[bool]]:
            # reverse bit_arr because LSB is arr_a[0] and MSB is arr_a[-1] in ALU
            bit_arr_a = bit_arr_a[::-1]
            bit_arr_b = bit_arr_b[::-1]
            a_i = utils.ba2int(bit_arr_a)
            b_i = utils.ba2int(bit_arr_b)
            sum_i = a_i + b_i + int(bit_c)
            sum_bit_arr = utils.int2ba(sum_i, 5)
            # reverse bit_arr because LSB is arr_a[0] and MSB is arr_a[-1] in ALU
            return sum_bit_arr[0], sum_bit_arr[1:][::-1]

        expected = tuple(_get_expected(*arg) for arg in args)
        all_assert_equal(self, expected, actuals)


if __name__ == '_main__':
    unittest.main()
