import numpy as np
from typing import Tuple
from nptyping import Array
import re

from src import CONFIG, utils


OP_PATTERN = re.compile(r'(\w+)')
IM_PATTERN = re.compile(r'^[01]{4}$')


INSTRUCTIONS = {
    # [MSB, ..., LSB]
    'MOV': {
        'A': {
            'Im': (False, False, True, True),
            'B': (False, False, False, True) + tuple(False for _ in range(4))
        },
        'B': {
            'Im': (False, True, True, True),
            'A': (False, True, False, False) + tuple(False for _ in range(4))
        }
    },
    'ADD': {
        'A': {
            'Im': (False, False, False, False),
        },
        'B': {
            'Im': (False, True, False, True),
        }
    },
    'IN': {
        'A': (False, False, True, False) + tuple(False for _ in range(4)),
        'B': (False, True, True, False) + tuple(False for _ in range(4))
    },
    'OUT': {
        'Im': (True, False, True, True),
        'B': (True, True, False, True) + tuple(False for _ in range(4))
    },
    'JMP': {
        'Im': (True, True, True, True)
    },
    'JNC': {
        'Im': (True, True, True, False)
    }
}


def assemble_line(line: str) -> Tuple[bool]:
    if len(line) == 0:
        raise ValueError('Invalid syntax: line {}; Empty line is not allow')

    code = OP_PATTERN.findall(line)
    if not (len(code) in (2, 3)):
        raise ValueError(
            'Invalid syntax: line {}; must be \"<INSTRUCTION> <OP1> <OP2> or <INSTRUCTION> <OP1>\"')

    try:
        if len(code) == 2:
            ins, op1 = code
            if IM_PATTERN.fullmatch(op1) is None:
                bit_arr = INSTRUCTIONS[ins][op1]
            else:
                bit_arr = INSTRUCTIONS[ins]['Im'] + utils.bastr2bat(op1)
        else:
            ins, op1, op2 = code
            if IM_PATTERN.fullmatch(op2) is None:
                bit_arr = INSTRUCTIONS[ins][op1][op2]
            else:
                bit_arr = INSTRUCTIONS[ins][op1]['Im'] + utils.bastr2bat(op2)
    except KeyError:
        raise ValueError('Invalid operation: line {}; No such a operation')

    # reverse because LSB is index = 0
    return bit_arr[::-1]


def assemble(program_path: str) -> Array[bool, 16, 8]:
    with open(program_path, 'r') as f:
        program = [l.strip() for l in f]

    if len(program) > 16:
        raise ValueError(
            'Program must be <= 16 lines because of ROM capacity.\n'
            + f'program path: {program_path}')

    if len(program) == 0:
        return np.full((16, 8), False)

    operations = []
    for i, line in enumerate(program, 1):
        try:
            ope = assemble_line(line)
        except ValueError as err:
            raise ValueError(str(err).format(i))
        operations.append(ope)
    padding = [tuple(False for _ in range(8)) for _ in range(16 - len(program))]
    operations += padding
    return np.array(operations)
