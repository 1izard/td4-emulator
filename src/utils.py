from numpy.testing import assert_array_equal
import numpy as np
from typing import Tuple
from nptyping import Array
import unittest
import itertools

from src import CONFIG


def bat2int(bit_arr: Tuple[bool]) -> int:
    bit_arr_str = ''.join(str(int(b)) for b in bit_arr)
    return int(bit_arr_str, 2)


def ba2int(bit_arr: Array[bool, 1, ...]) -> int:
    return bat2int(bit_arr)


def int2bastr(i: int, digit: int) -> str:
    return f'{i:0{digit}b}'


def bastr2bat(bit_arr_str: str) -> Tuple[bool]:
    return tuple(bool(int(s)) for s in bit_arr_str)


def bastr2ba(bit_arr_str: str) -> Array[bool, 1, ...]:
    return np.array(bastr2bat(bit_arr_str))


def int2bat(i: int, digit: int) -> Tuple[bool]:
    return bastr2bat(int2bastr(i, digit))


def int2ba(i: int, digit: int) -> Array[bool, 1, ...]:
    return bastr2ba(int2bastr(i, digit))


def gen_all_bool_patterns(length: int) -> Tuple[bool]:
    """Return all bool patterns. Be aware of the order of patterns.

    Arguments:
        length {int} -- bit length

    Returns:
        Tuple[Tuple[bool]] -- bool patterns (e.g, ((False, False), (False, True),
        (True, False), (True, True)))
    """
    tpls = tuple(((False, True)) for _ in range(length))
    return tuple(itertools.product(*tpls))


def all_assert_equal(test_case: unittest.TestCase, expecteds: Tuple, actuals: Tuple):
    """Exec assert equal for passed test patterns.

    Arguments:
        test_case {unittest.TestCase} -- TestUnit instance to exec assertEqual
        expecteds {Tuple} -- expected sequence
        actuals {Tuple} -- actual sequence
    """
    for e, a in zip(expecteds, actuals):
        test_case.assertEqual(e, a)


def all_assert_array_equal(expecteds: Tuple[Array[bool]], actuals: Tuple[Array[bool]]):
    for e, a in zip(expecteds, actuals):
        assert_array_equal(e, a)
