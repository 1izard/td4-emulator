from typing import Tuple
import functools


def NOT(x: bool) -> bool:
    return not x


def _AND(a: bool, b: bool) -> bool:
    return a and b


def AND(*xs: bool) -> bool:
    return functools.reduce(_AND, xs)


def _OR(a: bool, b: bool) -> bool:
    return a or b


def OR(*xs: bool) -> bool:
    return functools.reduce(_OR, xs)


def NAND(*xs: bool) -> bool:
    return NOT(AND(*xs))


def NOR(*xs: bool) -> bool:
    return NOT(OR(*xs))


def _XOR(a: bool, b: bool) -> bool:
    return OR(AND(a, NOT(b)), AND(NOT(a), b))


def XOR(*xs: bool) -> bool:
    return functools.reduce(_XOR, xs)


def HA(a: bool, b: bool) -> Tuple[bool, bool]:
    """Half Adder

    Arguments:
        a {bool} -- operand a
        b {bool} -- operand b

    Returns:
        Tuple[bool, bool] -- carry, sum
    """
    c = AND(a, b)
    s = XOR(a, b)
    return c, s


def FA(cin: bool, a: bool, b: bool) -> Tuple[bool, bool]:
    """Full Adder

    Arguments:
        cin {bool} -- input carry
        a {bool} -- operand a
        b {bool} -- operand b

    Returns:
        Tuple[bool, bool] -- carry, sum
    """
    t1_c, t1_s = HA(a, b)
    t2_c, t2_s = HA(cin, t1_s)
    c = OR(t2_c, t1_c)
    return c, t2_s


def ALU(cin: bool, arr_a: Tuple[bool], arr_b: Tuple[bool]) -> Tuple[bool, Tuple[bool]]:
    if arr_a is None or arr_b is None or len(arr_a) != 4 or len(arr_b) != 4:
        raise ValueError('Length of each input operands must be 4')

    c = cin

    def _FA():
        nonlocal c
        for a, b in zip(arr_a, arr_b):
            c, s = FA(c, a, b)
            yield s

    sums = tuple(_FA())
    return c, sums
