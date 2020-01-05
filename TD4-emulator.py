from src import CONFIG, ClockCycle, FrontMenu, units, utils, assembler, ui


def run_TD4(cc: ClockCycle):
    CLOCK_GENERATOR = units.build_CLOCK_GENERATOR(cc)
    ROM = units.build_ROM(assembler.assemble(CONFIG['program_file']))
    REGISTER_A = units.build_REGISTER(False, False)
    REGISTER_B = units.build_REGISTER(False, False)
    REGISTER_C = units.build_REGISTER(False, False)
    PC = units.build_REGISTER(True, True)
    D_FF_C = units.build_D_FF()

    q_d = utils.bastr2ba('0000')    # MUX input; cd is fixed with 0000
    q_c_in = utils.bastr2ba('0000')  # input of REGISTER_C is fixed with 0000
    step = 0
    max_step = CONFIG['max_step']
    for ck, reset in CLOCK_GENERATOR:
        if step > max_step or ck is False:
            break
        q_PC, q_a, q_b, q_c_out, c_flag = PC.send((ck, reset)), REGISTER_A.send((ck, reset)),\
            REGISTER_B.send((ck, reset)), REGISTER_C.send((ck, reset)), D_FF_C.send((ck, reset))
        op_arr = ROM(q_PC)
        decoded_arr = units.DECODER(op_arr[4:], units.NOT(c_flag))
        select_a, select_b, load0_, load1_, load2_, load3_ = \
            (bool(b) for b in decoded_arr)
        selected_arr = units.MUX(select_a, select_b, q_a, q_b, q_c_in, q_d)
        res_arr = units.ALU(c_flag, selected_arr, op_arr[:4])
        c, sum_arr = bool(res_arr[0]), res_arr[1:]
        D_FF_C.send(c)
        REGISTER_A.send((load0_, sum_arr))
        REGISTER_B.send((load1_, sum_arr))
        REGISTER_C.send((load2_, sum_arr))
        PC.send((load3_, sum_arr))
        units.DISPLAY(cc, **{
            'step': step, 'PC': utils.ba2str(q_PC[::-1]), 'output': utils.ba2str(q_c_out[::-1]),
            'REGISTER_A': utils.ba2str(q_a[::-1]), 'REGISTER_B': utils.ba2str(q_b[::-1]), 'c_flag': int(c_flag),
            'fetched_op': utils.ba2str(op_arr[::-1]), 'decode_res': utils.ba2str(decoded_arr), 'MUX_res': utils.ba2str(selected_arr[::-1]),
            'carry': int(c), 'ALU_res': utils.ba2str(sum_arr)})
        step += 1


def main():
    print('TD4 Power on...')
    ui.dummy_progress()

    while True:
        selected_front_menu = ui.front_menu()

        if selected_front_menu is FrontMenu.QUIT:
            print('TD4 Power off. See you...')
            break
        elif selected_front_menu is FrontMenu.RUN:
            selected_run_menu = ui.run_menu()
            try:
                run_TD4(selected_run_menu)
                print('\nFinish')
            except KeyboardInterrupt:
                pass
        else:
            raise ValueError('Undefined menu is selected')


if __name__ == '__main__':
    main()
