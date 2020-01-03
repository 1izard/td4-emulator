from numpy.testing import assert_array_equal
import numpy as np
from typing import Tuple, Callable
from nptyping import Array
import unittest
import os

from src import units, utils, assembler

gen_all_bool_patterns = utils.gen_all_bool_patterns
all_assert_equal = utils.all_assert_equal
ins = assembler.INSTRUCTIONS


class TestUnits(unittest.TestCase):
    def test_assemble_line_for_line_0(self):
        arg = ''
        actual = assembler.assemble_line(arg)
        expected = tuple(np.nan for _ in range(8))
        self.assertEqual(expected, actual)

    def test_assemble_line_for_correct_lines(self):
        args = (
            'MOV A 1010', 'MOV A B', 'MOV B 1010', 'MOV B A',
            'ADD A 1111', 'ADD B 0000',
            'IN A', 'IN B',
            'OUT 1010', 'OUT B',
            'JMP 1010',
            'JNC 1010',
        )
        actuals = (assembler.assemble_line(arg) for arg in args)
        es = (
            # MOV
            ins['MOV']['A']['Im'] + (True, False, True, False),
            ins['MOV']['A']['B'],
            ins['MOV']['B']['Im'] + (True, False, True, False),
            ins['MOV']['B']['A'],

            # ADD
            ins['ADD']['A']['Im'] + (True, True, True, True),
            ins['ADD']['B']['Im'] + (False, False, False, False),

            # IN
            ins['IN']['A'],
            ins['IN']['B'],

            # OUT
            ins['OUT']['Im'] + (True, False, True, False),
            ins['OUT']['B'],

            # JMP
            ins['JMP']['Im'] + (True, False, True, False),
            ins['JNC']['Im'] + (True, False, True, False)
        )
        expecteds = (e[::-1] for e in es)
        for e, a in zip(expecteds, actuals):
            self.assertEqual(e, a)

    def test_assemble_line_for_invalid_syntax(self):
        args = ('MOV A B 1010', 'MOV')
        for arg in args:
            with self.assertRaises(ValueError) as context:
                assembler.assemble_line(arg)
            self.assertTrue('Invalid syntax' in str(context.exception))

    def test_assemble_line_for_invalid_operation(self):
        args = ('MOV A C', 'JMP A')
        for arg in args:
            with self.assertRaises(ValueError) as context:
                assembler.assemble_line(arg)
            self.assertTrue('Invalid operation' in str(context.exception))

    def test_assemble_for_correct(self):
        arg = os.path.join(os.path.dirname(__file__), 'test_program_correct.txt')
        actual = assembler.assemble(arg)
        e = (
            ins['MOV']['A']['B'],
            tuple(np.nan for _ in range(8)),
            ins['MOV']['B']['Im'] + (True, False, True, False),
            ins['JMP']['Im'] + (True, False, True, False),
        )
        expected = np.array(tuple(t[::-1] for t in e) +
                            tuple(tuple(np.nan for _ in range(8)) for _ in range(12)))
        assert_array_equal(expected, actual)

    def test_assemble_for_over(self):
        arg = os.path.join(os.path.dirname(__file__), 'test_program_over.txt')
        with self.assertRaises(ValueError) as context:
            assembler.assemble(arg)
        self.assertTrue('Program must be <= 16' in str(context.exception))

    def test_assemble_for_invalid_syntax(self):
        arg = os.path.join(os.path.dirname(__file__), 'test_program_invalid_syntax.txt')
        with self.assertRaises(ValueError) as context:
            assembler.assemble(arg)
        self.assertTrue('Invalid syntax: line 1' in str(context.exception))

    def test_assemble_for_invalid_operation(self):
        arg = os.path.join(os.path.dirname(__file__), 'test_program_invalid_operation.txt')
        with self.assertRaises(ValueError) as context:
            assembler.assemble(arg)
        self.assertTrue('Invalid operation: line 1' in str(context.exception))
