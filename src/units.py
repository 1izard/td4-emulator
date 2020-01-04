import numpy as np
from nptyping import Array
from typing import Callable, Tuple
import functools
import time

from src import utils, ClockCycle


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
        -> Array[bool, 1, 5]:
    """ALU: 4-bit Full Adder

    Arguments:
        cin {bool} -- input carry
        arr_a {Array[bool, 1, 4]} -- 4-bit array as operand a
        arr_b {Array[bool, 1, 4]} -- 4-bit array as operand b

    Raises:
        ValueError: Length of arr_a and arr_b must be 4

    Returns:
        Array[bool, 1, 5] -- 0th bit is carry, others are sums (LSB is index=1, MSB is index=5)
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


def _MUX(a: bool, b: bool, c0: bool, c1: bool, c2: bool, c3: bool) -> bool:
    t0 = AND(c0, NOT(a), NOT(b))
    t1 = AND(c1, a, NOT(b))
    t2 = AND(c2, NOT(a), b)
    t3 = AND(c3, a, b)
    return OR(t0, t1, t2, t3)


def MUX(a: bool, b: bool,
        ca: Array[bool, 1, 4], cb: Array[bool, 1, 4], cc: Array[bool, 1, 4], cd: Array[bool, 1, 4])\
        -> Array[bool, 1, 4]:
    """4-input Multiplexer

    Arguments:
        a {bool} -- select a
        b {bool} -- select b
        ca {Array[bool, 1, 4]} -- 1st input 4-bit array
        cb {Array[bool, 1, 4]} -- 2nd input 4-bit array
        cc {Array[bool, 1, 4]} -- 3rd input 4-bit array
        cd {Array[bool, 1, 4]} -- 4th input 4-bit array

    Returns:
        Array[bool, 1, 4] -- Selected 4-bit array
    """
    return np.array(tuple(_MUX(a, b, ca[i], cb[i], cc[i], cd[i]) for i in range(4)))


def DECODER(op_arr: Array[bool, 1, 4], c_flag_: bool) -> Array[bool, 1, 6]:
    """Instruction Decoder

    Arguments:
        op_arr {Array[bool, 1, 4]} -- 4-bit operation code
        c_flag_ {bool} -- negative carry flag

    Returns:
        Array[bool, 1, 6] -- [select_a, select_b, load0_, load1_, load2_, load3_]
    """
    op0, op1, op2, op3 = op_arr
    select_a = OR(op0, op3)
    select_b = op1
    load0_ = OR(op2, op3)
    load1_ = OR(NOT(op2), op3)
    load2_ = NAND(NOT(op2), op3)
    load3_ = NAND(op2, op3, OR(op0, c_flag_))
    return np.array((select_a, select_b, load0_, load1_, load2_, load3_))


def build_REGISTER(ent: bool, enp: bool) -> Callable[[bool, Array[bool, 1, 4]], Array[bool, 1, 4]]:
    """Return register; 74HC161 as COUNTER or REGISTER

    Arguments:
        ent {bool} -- flag to decide which of COUNTER or REGISTER
        enp {bool} -- flag to decide which of COUNTER or REGISTER

    Raises:
        ValueError: raised when ent and enp are Not (True, True) or (False, False)

    Returns:
        Callable[[bool, Array[bool, 1, 4]], Array[bool, 1, 4]] -- COUNTER or REGISTER

    Yields:
        Callable[[bool, Array[bool, 1, 4]], Array[bool, 1, 4]] -- q; state of a register
    """
    def _COUNTER(load_: bool, reset_: bool, q: Array[bool, 1, 4]) -> Array[bool, 1, 4]:
        while True:
            ck = yield
            load_, reset_, input_arr = yield q  # return q when clock passed
            if load_ is False:
                q = input_arr
            else:
                res = ALU(False, q, utils.bastr2ba('1000'))  # count up
                q = res[1:]  # res[0] is carry
            if reset_ is False:
                q = utils.bastr2ba('0000')

    def _REGISTER(load_: bool, reset_: bool, q: Array[bool, 1, 4]) -> Array[bool, 1, 4]:
        while True:
            ck = yield
            load_, reset_, input_arr = yield q  # return q when clock passed
            if load_ is False:
                q = input_arr
            if reset_ is False:
                q = utils.bastr2ba('0000')

    if ent and enp:
        return _COUNTER(False, True, utils.bastr2ba('0000'))
    elif (ent is False) and (enp is False):
        return _REGISTER(False, True, utils.bastr2ba('0000'))
    else:
        raise ValueError('ent and enp are must be (True, True) or (False, False)')


def AR(address: Array[bool, 1, 4], g1_: bool, g2_: bool) -> Array[bool, 1, 16]:
    """Address Resolver. Convert 4-bit signal to one of 16 address for ROM.
    e.g, Returned (True, False, ..., False) implies 0th address in ROM.

    Arguments:
        a {bool} -- 0th bit
        b {bool} -- 1st bit
        c {bool} -- 2nd bit
        d {bool} -- 3rd bit
        g1 {bool} -- must be False
        g2 {bool} -- must be False

    Returns:
        Array[bool, 1, 16] -- Signal to spesify address of ROM (LSB is index=0)
    """
    a, b, c, d = address
    g = NOT(NAND(NOT(g1_), NOT(g2_)))
    t0 = NOT(NAND(NOT(a), NOT(b)))
    t1 = NOT(NAND(a, NOT(b)))
    t2 = NOT(NAND(NOT(a), b))
    t3 = NOT(NAND(a, b))
    t4 = NOT(NAND(NOT(c), NOT(d)))
    t5 = NOT(NAND(c, NOT(d)))
    t6 = NOT(NAND(NOT(c), d))
    t7 = NOT(NAND(c, d))
    return np.array([NOT(NAND(g, i, j)) for i in (t4, t5, t6, t7) for j in (t0, t1, t2, t3)])


def build_ROM(bit_matrix: Array[bool, 16, 8]) -> Callable[[Array[bool, 1, 4]], Array[bool, 1, 8]]:
    """Make ROM

    Arguments:
        bit_matrix {Array[bool, 16, 8]} -- memory

    Returns:
        Callable[[Array[bool, 1, 4]], Array[bool, 1, 8]] -- ROM
    """
    def _ROM(address: Array[bool, 1, 4]) -> Array[bool, 1, 8]:
        return bit_matrix[AR(address, False, False)][0]

    return _ROM


def build_CLOCK_GENERATOR(cc: ClockCycle) -> Callable[[], Tuple[bool, bool]]:
    """Build Clock Generator

    Arguments:
        cc {ClockCycle} -- Clock Cycle defined in Enum: ClockCycle

    Returns:
        Callable[[], Tuple[bool, bool]] -- CLOCK_GENERATOR
    """
    def _AUTO_CLOCK_GENERATOR():
        while True:
            time.sleep(1 / cc.value)
            clock, reset = True, True
            yield clock, reset

    # TODO
    def _MANUAL_CLOCK_GENERATOR():
        while True:
            print('> ', end=' ')
            s = input().split()
            print(s)
            clock, reset = True, True
            yield clock, reset

    if cc in (ClockCycle.NORMAL, ClockCycle.HIGH):
        return _AUTO_CLOCK_GENERATOR
    else:
        return _MANUAL_CLOCK_GENERATOR
