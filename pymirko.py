#!/usr/bin/env python
"""
MIRKO post processing tools

2016 Xaratustrah

"""

import sys, os, argparse, glob
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt
import fortranformat as ff

MIRKO = 'mirko'
EVET_LOOPS = 10
N_TURNS = 3
MIX_FILE = 'esr_2016-04.mix'
TEMP_FILENAME = 'temp.mak'
MIXFILE_PLACEHOLDER = 'MIXFILE_PLACEHOLDER'
PLACEHOLDER = 'NUMBERPLACEHOLDER'
FILENAME_PLACEHOLDER = 'FILENAME_PLACEHOLDER'

LAST_RING_ELEMENT = 330


def get_apreture_dic():
    ffline = ff.FortranRecordReader('(3X,a16,3I4,F17.4,F17.10,2F12.3,I4,2x,a16)')
    dic = {}
    with open(MIX_FILE) as f:
        for _ in range(31):
            next(f)
        # for i in range(LAST_RING_ELEMENT):
        while True:
            try:
                line = f.readline()
                if not line:
                    break
                hh = ffline.read(line)
                device_type = int(hh[2])
                if device_type == 2:
                    # this is a drift space, ignore it
                    continue
                    # name = 'DRIFT'
                else:
                    name = hh[0].strip()
                aperture = hh[6]
                if name not in dic:
                    dic.update({name: aperture})
                    # print('{},\t{},\t,{}\n'.format(name, device_type, aperture))
                    # if aperture == 0:
                    #    print(name)
            except:
                pass
    return dic


def loop_mirko(generator_filename):
    print('Using MIX file {}.'.format(MIX_FILE))
    for i in range(1, EVET_LOOPS + 1):
        create_mak_file(i, generator_filename, N_TURNS)
        cmd = MIRKO.split()
        cmd.append(TEMP_FILENAME)
        print('Running MIRKO for event at element No. {}.'.format(i))
        call(cmd)
        os.remove(TEMP_FILENAME)


def create_mak_file(current_idx, generator_filename, n_turns=1):
    # read the header section from a file
    with open(generator_filename) as f:
        header_section = f.read()

    repeat_section = ''.join('aenv,{},{}\n*\n'.format(i, i) for i in range(1, 365 + 1))
    middle_section = 'savs,less,penv,,delp,\n*\n'
    final_section = 'close,9\n*\npnul,solb,0,0,0,0,0,-0.009,sync\n'

    with open(TEMP_FILENAME, 'w') as f:
        new_head = header_section.replace(PLACEHOLDER, '{}'.format(current_idx)).replace(MIXFILE_PLACEHOLDER,
                                                                                         '{}'.format(MIX_FILE)).replace(
            FILENAME_PLACEHOLDER, 'result_at_{:03d}.txt'.format(current_idx))
        f.write(new_head)
        for i in range(n_turns):
            f.write(repeat_section)
            f.write(middle_section)
        f.write(final_section)


def get_data_from_result_file(filename):
    dic = get_apreture_dic()
    arr = np.array([])
    arr_of_z_at_ends = np.array([])

    current_turn_number = 1
    z_at_end = 0
    with open(filename) as f:
        for line in f:
            s = line.split()
            if not len(s) == 6:
                continue
            try:
                number = int(s[-6])
                z = float(s[-4])
                # add the circumference BEFORE checking last element
                z_cont = z + z_at_end
                # check for last element now
                if number == LAST_RING_ELEMENT:
                    # this is really cool:
                    z_at_end += z
                    arr_of_z_at_ends = np.append(arr_of_z_at_ends, z_at_end)
                    current_turn_number += 1
                up = float(s[-3])
                down = float(s[-2])
                ref = float(s[-1])
                # do this one at last, to make advantage of try/except block
                aperture = dic[s[-5].strip()]
                arr = np.append(arr, (number, aperture, z, z_cont, up, down, ref, current_turn_number))

            except(ValueError, IndexError, KeyError):
                # boah!
                pass
    arr = np.reshape(arr, (int(len(arr)) / 8, 8))

    return arr, arr_of_z_at_ends


def check_particle_loss(arr):
    el_number = 0
    loss_z_cont = 0
    loss_ref = 0
    current_turn_number = 0
    for i in range(np.shape(arr)[0]):
        # check if the particle hits the aperture
        if arr[i, 4] >= arr[i, 1] or arr[i, 5] < (-1 * arr[i, 1]):
            # determine loss position using z_cont
            el_number, loss_z_cont, loss_ref, current_turn_number = int(arr[i, 0]), arr[i, 3], arr[i, 6], int(arr[i, 7])
    return el_number, loss_z_cont, loss_ref, current_turn_number


def check_particle_at_element(arr, element_number, element_x_min, element_x_max):
    pock_z = np.array([])
    pock_x = np.array([])
    current_turn_number_array = np.array([])

    for i in range(np.shape(arr)[0]):
        # check the position of particle at a specific element
        if arr[i, 0] == element_number:
            pock_z = np.append(pock_z, arr[i, 3])
            current_turn_number_array = np.append(current_turn_number_array, arr[i, 7])
            if arr[i, 6] >= element_x_min and arr[i, 6] <= element_x_max:
                print('Turn {}: Particle hits pocket detector (element number {} at {}mm).'.format(int(arr[i, 7]),
                                                                                                   element_number,
                                                                                                   arr[i, 6]))
                pock_x = np.append(pock_x, arr[i, 6])
                # we already found a hit, so quit
                break
            else:
                print('Turn {}: Particle misses pocket detector (element number {}).'.format(int(arr[i, 7]),
                                                                                             element_number))
                pock_x = np.append(pock_x, 0)
    return pock_z, pock_x, current_turn_number_array


def save_to_file(arr):
    np.savetxt('result_array.txt', arr, delimiter=',')


# --------------------

def plot_data(arr, arr_of_z_at_ends, filename):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # plot lines first
    ax.plot(arr[:, 3], arr[:, 4], 'g-')
    ax.plot(arr[:, 3], arr[:, 6], 'b-.')
    ax.plot(arr[:, 3], arr[:, 5], 'g-')

    # plot vertical lines for turns
    for i in range(len(arr_of_z_at_ends)):
        plt.axvline(arr_of_z_at_ends[i], color='b', linestyle='--')

    # find loss point
    el_number, loss_z_cont, loss_ref, current_turn_number = check_particle_loss(arr)
    if el_number == 0 and loss_z_cont == 0 and loss_ref == 0:
        print('Particle would survive for all turns if no pocket detectors were inside.')
    else:
        print('Particle is lost at element number.'.format(el_number))
        ax.plot(loss_z_cont, loss_ref, 'rv')

    # check position at pocket detector which is element 229
    pock_z, pock_x, current_turn_number_array = check_particle_at_element(arr, 229, 22, 82)
    for i in range(len(pock_z)):
        ax.axvline(pock_z[i], color='r', linestyle='--')

        if pock_x[i] != 0:
            ax.plot(pock_z[i], pock_x[i], 'rD')
            ax.annotate('Pocket detector hit (turn {})'.format(int(current_turn_number_array[i])),
                        xy=(pock_z[i], pock_x[i]), xytext=(0.4, 0.8),
                        textcoords='figure fraction',
                        xycoords='data',
                        arrowprops=dict(width=1, headwidth=5, edgecolor='blue', facecolor='blue', shrink=0.05))
        else:
            ax.plot(pock_z[i], pock_x[i], 'rx')

    # finalize the plot
    plt.grid(True)
    plt.xlabel('Path [mm]')
    plt.ylabel('Offset [mm]')
    filename_wo_ext = os.path.splitext(filename)[0]
    plt.title(filename_wo_ext)
    fig.savefig(os.path.splitext(filename_wo_ext)[0] + '.png', dpi=400)
    # plt.show()


def main():
    parser = argparse.ArgumentParser(prog='pymirko')
    parser.add_argument('--verbose', action='store_true', help='Increase verbosity.')

    parser.add_argument('--loop', action='store_true', help='Loop MIRKO.')
    parser.add_argument('--plot', action='store_true', help='Plot results file.')
    parser.add_argument('--check', action='store_true', help='Only check misses and hits.')
    parser.add_argument('--many', action='store_true', help='Plot loop.')
    parser.add_argument('filename', nargs=1, type=str, help='Input file name.')

    args = parser.parse_args()
    # check the first switches

    filename = args.filename[0]
    if not os.path.exists(filename):
        print('Please enter a valid filename.')
        return

    if args.loop and args.plot:
        parser.print_help()
        return

    if args.loop:
        loop_mirko(filename)

    if args.plot:
        arr, arr_of_z_at_ends = get_data_from_result_file(filename)
        save_to_file(arr)
        plot_data(arr, arr_of_z_at_ends, filename)

    if args.check:
        arr, _ = get_data_from_result_file(filename)
        check_particle_at_element(arr, 229, 22, 82)

    if args.many:
        for file in glob.glob("result_at_*.txt"):
            print(file)
            arr, arr_of_z_at_ends = get_data_from_result_file(file)
            # check_particle_at_element(arr, 229, 22, 82)
            plot_data(arr, arr_of_z_at_ends, file)


# --------------------
if __name__ == '__main__':
    main()
