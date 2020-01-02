from typing import Tuple
import unittest
import itertools


def ba2int(bit_arr: Tuple[bool]) -> int:
    bit_arr_str = ''.join(str(int(b)) for b in bit_arr)
    return int(bit_arr_str, 2)


def int2bastr(i: int, digit: int) -> str:
    return f'{i:0{digit}b}'


def bastr2ba(bit_arr_str: str) -> Tuple[bool]:
    return tuple(bool(int(s)) for s in bit_arr_str)


def int2ba(i: int, digit: int) -> Tuple[bool]:
    return bastr2ba(int2bastr(i, digit))


def gen_all_bool_patterns(length: int) -> Tuple[Tuple[bool]]:
    """Return all bool patterns. Be aware of the order of patterns.

    Arguments:
        length {int} -- bit length

    Returns:
        Tuple[Tuple[bool]] -- bool patterns (e.g, ((False, False), (False, True),
        (True, False), (True, True)))
    """
    tpls = tuple((False, True) for _ in range(length))
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
