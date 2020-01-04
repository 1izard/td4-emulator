from src import CONFIG, ClockCycle, units, utils, assembler


def main():
    CLOCK_GENERATOR = units.build_CLOCK_GENERATOR(ClockCycle.NORMAL)
    ROM = units.build_ROM(assembler.assemble(CONFIG['program_file']))
    REGISTER_A = units.build_REGISTER(False, False)
    REGISTER_B = units.build_REGISTER(False, False)
    REGISTER_C = units.build_REGISTER(False, False)
    PC = units.build_REGISTER(True, True)
    D_FF_C = units.build_D_FF()

    q_d = utils.bastr2ba('0000')    # MUX input; cd is fixed with 0000
    q_c_in = utils.bastr2ba('0000')
    count = -1
    for ck, reset in CLOCK_GENERATOR:
        q_PC, q_a, q_b, q_c_out, c_flag = PC.send((ck, reset)), REGISTER_A.send((ck, reset)),\
            REGISTER_B.send((ck, reset)), REGISTER_C.send((ck, reset)), D_FF_C.send((ck, reset))
        print(f'count: {count}, q_c_out: {q_c_out}')
        op_arr = ROM(q_PC)
        select_a, select_b, load0_, load1_, load2_, load3_ = \
            (bool(b) for b in units.DECODER(op_arr[4:], units.NOT(c_flag)))
        selected_arr = units.MUX(select_a, select_b, q_a, q_b, q_c_in, q_d)
        res_arr = units.ALU(c_flag, selected_arr, op_arr[:4])
        c, sum_arr = bool(res_arr[0]), res_arr[1:]
        D_FF_C.send(c)
        REGISTER_A.send((load0_, sum_arr))
        REGISTER_B.send((load1_, sum_arr))
        REGISTER_C.send((load2_, sum_arr))
        PC.send((load3_, sum_arr))
        if count == 200:
            break
        count += 1


if __name__ == '__main__':
    main()
