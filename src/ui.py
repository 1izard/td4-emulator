from tqdm import trange
import time
import re

from src import ClockCycle, FrontMenu, DebugMenu


def dummy_progress():
    for i in trange(100):
        time.sleep(0.02)


def menu_io(menu_str: str, max_menu_num: int) -> int:
    menu_num_pattern = re.compile(r'^[0-' f'{max_menu_num}]$')
    while True:
        print(menu_str, end=' ')
        input_str = input().strip()
        if menu_num_pattern.fullmatch(input_str):
            break
        else:
            print(f'Input number from 0 to {max_menu_num}')
    return int(input_str)


def front_menu() -> FrontMenu:
    front_menus = tuple(FrontMenu.__members__.items())

    front_menu_str = ''
    for i, menu in enumerate(front_menus):
        front_menu_str += f'[{i}] {menu[0]}  '
    front_menu_str += '> '

    max_front_menu_num = len(front_menus) - 1
    selected = menu_io(front_menu_str, max_front_menu_num)
    return front_menus[selected][1]


def run_menu() -> ClockCycle:
    clock_cycles = tuple(ClockCycle.__members__.items())

    run_menu_str = ''
    for i, cc in enumerate(clock_cycles):
        run_menu_str += f'[{i}] {cc[0]}'
        run_menu_str += f'({cc[1].value}Hz)  ' if cc[1].value > 0 else '  '
    run_menu_str += '> '

    max_run_menu_num = len(clock_cycles) - 1
    selected = menu_io(run_menu_str, max_run_menu_num)
    return clock_cycles[selected][1]


def debug_menu() -> DebugMenu:
    debug_menus = tuple(DebugMenu.__members__.items())

    debug_menu_str = ''
    for i, menu in enumerate(debug_menus):
        debug_menu_str += f'[Enter or {i}] ' if menu[1] is DebugMenu.NEXT else f'[{i}] '
        debug_menu_str += f'{menu[0]}  '
    debug_menu_str += '> '

    max_debug_menu_num = len(debug_menus) - 1
    debug_menu_num_pattern = re.compile(r'^[0-' f'{max_debug_menu_num}]$')
    while True:
        print(debug_menu_str, end=' ')
        input_str = input().strip()
        if input_str is None or len(input_str) == 0:
            return DebugMenu.NEXT
        if debug_menu_num_pattern.fullmatch(input_str):
            selected = int(input_str)
            return debug_menus[selected][1]
        else:
            print(f'Input number from 0 to {max_debug_menu_num}')
