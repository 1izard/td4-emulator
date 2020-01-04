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
        args = ((np.array(p[::-1]), 0, 0) for p in patterns)
        actuals = np.array(tuple(units.AR(*arg) for arg in args))
        e = [[False for _ in range(16)] for _ in range(16)]
        for i in range(16):
            e[i][i] = True
        expected = np.array(e)
        assert_array_equal(expected, actuals)

    def test__MUX(self):
        args = (
            # c0
            (False, False) + (False, False, False, False),
            (False, False) + (False, True, False, False),

            (False, False) + (True, False, False, False),
            (False, False) + (True, True, False, False),

            # c1
            (True, False) + (False, False, False, False),
            (True, False) + (False, False, True, False),

            (True, False) + (False, True, False, False),
            (True, False) + (False, True, True, False),

            # c2
            (False, True) + (False, False, False, False),
            (False, True) + (False, False, False, True),

            (False, True) + (False, False, True, False),
            (False, True) + (False, False, True, True),

            # c3
            (True, True) + (False, False, False, False),
            (True, True) + (True, False, False, False),

            (True, True) + (False, False, False, True),
            (True, True) + (True, False, False, True),
        )
        actuals = (units._MUX(*arg) for arg in args)
        expecteds = (False, False, True, True) * 4
        for e, a in zip(actuals, expecteds):
            self.assertEqual(e, a)

    def test_MUX(self):
        args = (
            # c0
            (False, False, utils.bastr2ba('1010'), utils.bastr2ba('1011'),
                utils.bastr2ba('1100'), utils.bastr2ba('1101')),

            # c1
            (True, False, utils.bastr2ba('1010'), utils.bastr2ba('1011'),
                utils.bastr2ba('1100'), utils.bastr2ba('1101')),

            # c2
            (False, True, utils.bastr2ba('1010'), utils.bastr2ba('1011'),
                utils.bastr2ba('1100'), utils.bastr2ba('1101')),

            # c3
            (True, True, utils.bastr2ba('1010'), utils.bastr2ba('1011'),
                utils.bastr2ba('1100'), utils.bastr2ba('1101')),
        )
        actuals = (units.MUX(*arg) for arg in args)
        expecteds = (utils.bastr2ba('1010'), utils.bastr2ba('1011'),
                     utils.bastr2ba('1100'), utils.bastr2ba('1101'))
        for e, a in zip(expecteds, actuals):
            assert_array_equal(e, a)

    def test_DECODER(self):
        args = (
            (utils.bastr2ba('0011')[::-1], False),  # MOV A Im
            (utils.bastr2ba('0111')[::-1], False),  # MOV B Im
            (utils.bastr2ba('0001')[::-1], False),  # MOV A B
            (utils.bastr2ba('0100')[::-1], False),  # MOV B A
            (utils.bastr2ba('0000')[::-1], False),  # ADD A Im
            (utils.bastr2ba('0101')[::-1], False),  # ADD B Im
            (utils.bastr2ba('0010')[::-1], False),  # IN A
            (utils.bastr2ba('0110')[::-1], False),  # IN B
            (utils.bastr2ba('1011')[::-1], False),  # OUT Im
            (utils.bastr2ba('1001')[::-1], False),  # OUT B
            (utils.bastr2ba('1111')[::-1], False),  # JMP Im
            (utils.bastr2ba('1110')[::-1], True),  # JNC Im with c = 0; c_flog_ = 1
            (utils.bastr2ba('1110')[::-1], False),  # JNC Im with c = 1; c_flog_ = 0
        )
        actuals = (units.DECODER(*arg) for arg in args)
        expecteds = (
            utils.bastr2ba('110111'),  # MOV A Im
            utils.bastr2ba('111011'),  # MOV B Im
            utils.bastr2ba('100111'),  # MOV A B
            utils.bastr2ba('001011'),  # MOV B A
            utils.bastr2ba('000111'),  # ADD A Im
            utils.bastr2ba('101011'),  # ADD B Im
            utils.bastr2ba('010111'),  # IN A
            utils.bastr2ba('011011'),  # IN B
            utils.bastr2ba('111101'),  # OUT Im
            utils.bastr2ba('101101'),  # OUT B
            utils.bastr2ba('111110'),  # JMP Im
            utils.bastr2ba('111110'),  # JNC Im with c = 0
            utils.bastr2ba('111111'),  # JNC Im with c = 1 (xx1111 is OK)
        )
        for e, a in zip(expecteds, actuals):
            assert_array_equal(e, a)

    def test_build_REGISTER_for_invalid_ent_and_enp(self):
        with self.assertRaises(ValueError) as context:
            units.build_REGISTER(False, True)
        self.assertTrue(
            'ent and enp are must be (True, True) or (False, False)' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            units.build_REGISTER(True, False)
        self.assertTrue(
            'ent and enp are must be (True, True) or (False, False)' in str(context.exception))

    def test_build_REGISTER_for_COUNTER(self):
        args = (True, True)
        COUNTER = units.build_REGISTER(*args)
        next(COUNTER)

        # count
        COUNTER.send((True, True))
        COUNTER.send((True, utils.bastr2ba('1010')[::-1]))
        actual = COUNTER.send((True, True))
        expected = utils.bastr2ba('0001')[::-1]
        assert_array_equal(expected, actual)

        # load
        COUNTER.send((False, utils.bastr2ba('0101')[::-1]))
        actual = COUNTER.send((True, True))
        expected = utils.bastr2ba('0101')[::-1]
        assert_array_equal(expected, actual)

        # count
        COUNTER.send((True, utils.bastr2ba('1010')[::-1]))
        actual = COUNTER.send((True, True))
        expected = utils.bastr2ba('0110')[::-1]
        assert_array_equal(expected, actual)

        # reset
        COUNTER.send((True, utils.bastr2ba('1010')[::-1]))
        COUNTER.send((True, False))
        COUNTER.send((True, utils.bastr2ba('1010')[::-1]))
        actual = COUNTER.send((True, True))
        expected = utils.bastr2ba('0000')[::-1]
        assert_array_equal(expected, actual)

    def test_build_REGISTER_for_REGISTER(self):
        args = (False, False)
        REGISTER = units.build_REGISTER(*args)
        next(REGISTER)

        # load
        REGISTER.send((True, True))
        REGISTER.send((False, utils.bastr2ba('1010')[::-1]))
        actual = REGISTER.send((True, True))
        expected = utils.bastr2ba('1010')[::-1]
        assert_array_equal(expected, actual)

        # hold
        REGISTER.send((True, utils.bastr2ba('0101')[::-1]))
        actual = REGISTER.send((True, True))
        expected = utils.bastr2ba('1010')[::-1]   # must be previous state
        assert_array_equal(expected, actual)

        # hold
        REGISTER.send((True, utils.bastr2ba('0000')[::-1]))
        actual = REGISTER.send((True, True))
        expected = utils.bastr2ba('1010')[::-1]   # must be previous state
        assert_array_equal(expected, actual)

        # reset
        REGISTER.send((True, utils.bastr2ba('1010')[::-1]))
        REGISTER.send((True, False))
        REGISTER.send((True, utils.bastr2ba('1010')[::-1]))
        actual = REGISTER.send((True, True))
        expected = utils.bastr2ba('0000')[::-1]
        assert_array_equal(expected, actual)

    def test_build_ROM(self):
        _arg = np.array(tuple(utils.int2bat(i, 8) for i in range(16)))
        ROM = units.build_ROM(_arg)

        # line 0
        arg = utils.bastr2ba('0000')[::-1]
        actual = ROM(arg)
        expected = _arg[0]
        assert_array_equal(expected, actual)

        # line 5
        arg = utils.bastr2ba('0101')[::-1]
        actual = ROM(arg)
        expected = _arg[5]
        assert_array_equal(expected, actual)

        # line 11
        arg = utils.bastr2ba('1011')[::-1]
        actual = ROM(arg)
        expected = _arg[11]
        assert_array_equal(expected, actual)


if __name__ == '_main__':
    unittest.main()
