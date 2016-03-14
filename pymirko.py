#!/usr/bin/env python
"""
MIRKO post processing tools

2016 Xaratustrah

"""

import sys, os, argparse
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt

MIRKO = 'mirko'
EVET_LOOPS = 2
N_TURNS = 2
MIX_FILE = 'origin.mix'
TEMP_FILENAME = 'temp.mak'
MIXFILE_PLACEHOLDER = 'MIXFILE_PLACEHOLDER'
PLACEHOLDER = 'NUMBERPLACEHOLDER'


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
    arr = np.array([])
    filename = filename
    with open(filename) as f:
        for line in f:
            s = line.split()
            if not len(s) == 6:
                continue
            try:
                # todo: element number 355 contains the last coordinate.
                # todo: element names should be checked with dictionary

                arr = np.append(arr, (int(s[-6]), float(s[-4]), float(s[-3]), float(s[-2]), float(s[-1])))
            except(ValueError, IndexError):
                pass
    arr = np.reshape(arr, (int(len(arr)) / 5, 5))

    return arr


def plot_data(arr, filename):
    plt.plot(arr[:, 1], arr[:, 2], 'r-')
    plt.plot(arr[:, 1], arr[:, 4], 'b-.')
    plt.plot(arr[:, 1], arr[:, 3], 'g-')
    plt.grid(True)
    plt.xlabel('Path [mm]')
    plt.ylabel('Offset [mm]')
    plt.title(filename)
    plt.show()


def main():
    parser = argparse.ArgumentParser(prog='pymirko')
    parser.add_argument('--verbose', action='store_true', help='Increase verbosity.')

    parser.add_argument('--loop', action='store_true', help='Loop MIRKO.')
    parser.add_argument('--plot', action='store_true', help='Plot results file.')
    parser.add_argument('filename', nargs=1, type=str, help='Input file name.')

    args = parser.parse_args()
    # check the first switches

    filename = args.filename[0]

    if args.loop and args.plot:
        parser.print_help()
        return

    if args.loop:
        loop_mirko(filename)

    if args.plot:
        arr = get_data_from_result_file(filename)
        # print(arr)
        plot_data(arr, filename)
        np.savetxt('array.txt', arr, delimiter=',')


# --------------------
if __name__ == '__main__':
    main()
