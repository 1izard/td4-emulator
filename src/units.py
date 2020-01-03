import numpy as np
from nptyping import Array
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


def HA(a: bool, b: bool) -> Array[bool, 1, 2]:
    """Half Adder

    Arguments:
        a {bool} -- operand a
        b {bool} -- operand b

    Returns:
        Tuple[bool, bool] -- carry, sum
    """
    c = AND(a, b)
    s = XOR(a, b)
    return np.array((c, s))


def FA(cin: bool, a: bool, b: bool) -> Array[bool, 1, 2]:
    """Full Adder

    Arguments:
        cin {bool} -- input carry
        a {bool} -- operand a
        b {bool} -- operand b

    Returns:
        Array[bool, 1, 2] -- carry, sum
    """
    t1_c, t1_s = HA(a, b)
    t2_c, t2_s = HA(cin, t1_s)
    c = OR(t2_c, t1_c)
    return np.array((c, t2_s))


def ALU(cin: bool, arr_a: Array[bool, 1, 4], arr_b: Array[bool, 1, 4]) \
        -> Array[bool, 1, 9]:
    """ALU: 4-bit Full Adder

    Raises:
        ValueError: Length of arr_a and arr_b must be 4

    Returns:
        Array[bool, 1, 9] -- 0th bit is carry, others are sums (LSB is index=1, MSB is index=9)
    """
    if arr_a is None or arr_b is None or len(arr_a) != 4 or len(arr_b) != 4:
        raise ValueError('Length of each input operands must be 4')

    c = cin

    def _FA():
        nonlocal c
        for a, b in zip(arr_a, arr_b):
            c, s = FA(c, a, b)
            yield s

    sums = tuple(_FA())
    return np.array((c,) + sums)


def AR(a: bool, b: bool, c: bool, d: bool, g1: bool, g2: bool) -> Array[bool, 1, 16]:
    """Address Resolver. Convert 4-bit signal to one of 16 address for ROM.
    e.g, Returned (True, False, ..., False) implies 0th address in ROM.

    Arguments:
        a {bool} -- 0th bit
        b {bool} -- 1st bit
        c {bool} -- 2nd bit
        d {bool} -- 3rd bit
        g1 {bool} -- must be True
        g2 {bool} -- must be True

    Returns:
        Array[bool, 1, 16] -- Signal to spesify address of ROM (LSB is index=0)
    """
    g = NOT(NAND(g1, g2))
    t0 = NOT(NAND(NOT(a), NOT(b)))
    t1 = NOT(NAND(a, NOT(b)))
    t2 = NOT(NAND(NOT(a), b))
    t3 = NOT(NAND(a, b))
    t4 = NOT(NAND(NOT(c), NOT(d)))
    t5 = NOT(NAND(c, NOT(d)))
    t6 = NOT(NAND(NOT(c), d))
    t7 = NOT(NAND(c, d))
    return np.array([NOT(NAND(g, i, j)) for i in (t4, t5, t6, t7) for j in (t0, t1, t2, t3)])
