#!/usr/bin/env python
"""
MIRKO post processing tools

2016 Xaratustrah

"""

import sys, os
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt

TEMP_FILENAME = 'temp.mak'
MIRKO = 'java -jar ../../jMirko/dist/jMirko.jar'
PLACEHOLDER = 'NUMBERPLACEHOLDER'
EVET_LOOPS = 365
N_TURNS = 2


def loop_mirko(generator_filename):
    for i in range(EVET_LOOPS):
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

    repeat_section = ''.join('aenv,{},{}\n*'.format(i, i) for i in range(1, 365 + 1))
    middle_section = 'savs,less,penv,,delp,\n*'
    final_section = 'close,9\n*\npnul,solb,0,0,0,0,0,-0.009,sync\n'

    with open(TEMP_FILENAME, 'w') as f:
        f.write(header_section.replace(PLACEHOLDER, '{}'.format(idx)))
        for i in range(n_turns):
            f.write(repeat_section)
            f.write(middle_section)
        f.write(final_section)


def get_data_from_resultfile(filename):
    arr = np.array([])
    filename = filename
    with open(filename) as f:
        for line in f:
            s = line.split()
            if not len(s) == 6:
                continue
            try:
                arr = np.append(arr, (int(s[-6]), float(s[-4]), float(s[-3]), float(s[-2]), float(s[-1])))
            except(ValueError, IndexError):
                pass
    arr = np.reshape(arr, (int(len(arr)) / 5, 5))

    return arr


def plot_data(arr, filename):
    plt.plot(arr[:, 0], arr[:, 3], 'b-')
    plt.plot(arr[:, 0], arr[:, 2], 'g-')
    plt.plot(arr[:, 0], arr[:, 1], 'r-')
    plt.grid(True)
    plt.xlabel('Path [mm]')
    plt.ylabel('Offset [mm]')
    plt.title(filename)
    plt.show()


def main():
    try:
        filename = sys.argv[1]
    except(IndexError):
        print('Please provide filename.')
        return

    loop_mirko(filename)
    arr = get_data_from_resultfile(filename)
    print(arr)
    # plot_data(arr, filename)


# --------------------
if __name__ == '__main__':
    main()
