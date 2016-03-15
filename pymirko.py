#!/usr/bin/env python
"""
MIRKO post processing tools

2016 Xaratustrah

"""

import sys, os, argparse
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt
import fortranformat as ff

MIRKO = 'mirko'
EVET_LOOPS = 4
N_TURNS = 4
MIX_FILE = 'origin.mix'
TEMP_FILENAME = 'temp.mak'
MIXFILE_PLACEHOLDER = 'MIXFILE_PLACEHOLDER'
PLACEHOLDER = 'NUMBERPLACEHOLDER'
LAST_RING_ELEMENT = 355


def get_apreture_dic():
    ffline = ff.FortranRecordReader('(3X,a16,3I4,F17.4,F17.10,2F12.3,I4,2x,a16)')
    dic = {}
    with open(MIX_FILE) as f:
        for _ in range(31):
            next(f)
        for i in range(355):
            try:
                line = f.readline()
                hh = ffline.read(line)
                if hh[0].strip() == '':
                    name = 'DRIFT'
                else:
                    name = hh[0].strip()
                aperture = hh[6]
                if name not in dic:
                    dic.update({name: aperture})
            except:
                pass
    return dic


def loop_mirko(generator_filename):
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
                                                                                         '{}'.format(MIX_FILE))
        f.write(new_head)
        for i in range(n_turns):
            f.write(repeat_section)
            f.write(middle_section)
        f.write(final_section)


def get_data_from_result_file(filename):
    dic = get_apreture_dic()
    arr = np.array([])
    z_at_end = 0
    with open(filename) as f:
        for line in f:
            s = line.split()
            if not len(s) == 6:
                continue
            try:
                number = int(s[-6])
                z = float(s[-4])
                if number == LAST_RING_ELEMENT:
                    # this is really cool:
                    z_at_end += z
                z_cont = z + z_at_end
                up = float(s[-3])
                down = float(s[-2])
                ref = float(s[-1])
                # do this one at last, to make advantage of try/except block
                aperture = dic[s[-5].strip()]
                arr = np.append(arr, (number, aperture, z, z_cont, up, down, ref))
            except(ValueError, IndexError, KeyError):
                # boah!
                pass
    arr = np.reshape(arr, (int(len(arr)) / 7, 7))

    return arr


def check_particle_loss(arr):
    for i in range(np.shape(arr)[0]):
        # check if the particle hits the aperture
        if arr[i, 4] >= arr[i, 1] or arr[i, 4] < (-1 * arr[i, 1]):
            # return loss position
            # print('Particle lost at: {}mm'.format(arr[i, 2]))
            return (arr[i, 2], arr[i, 4])


def plot_data(arr, filename):
    loss_z, loss_up = check_particle_loss(arr)
    plt.plot(arr[:, 3], arr[:, 4], 'g-')
    plt.plot(arr[:, 3], arr[:, 6], 'b-.')
    plt.plot(arr[:, 3], arr[:, 5], 'g-')
    plt.plot(loss_z, loss_up, 'rv')
    plt.grid(True)
    plt.xlabel('Path [mm]')
    plt.ylabel('Offset [mm]')
    plt.title(filename)
    plt.show()


def save_to_file(arr):
    np.savetxt('array.txt', arr, delimiter=',')


def main():
    parser = argparse.ArgumentParser(prog='pymirko')
    parser.add_argument('--verbose', action='store_true', help='Increase verbosity.')

    parser.add_argument('--loop', action='store_true', help='Loop MIRKO.')
    parser.add_argument('--plot', action='store_true', help='Plot results file.')
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
        arr = get_data_from_result_file(filename)
        # save_to_file(arr)
        # check_particle_loss(arr)
        plot_data(arr, filename)


# --------------------
if __name__ == '__main__':
    main()
