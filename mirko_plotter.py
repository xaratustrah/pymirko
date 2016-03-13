#!/usr/bin/env python
"""
MIRKO results plotter script

2016 Xaratustrah

"""

import sys
import numpy as np
import matplotlib.pyplot as plt


def main():
    arr = np.array([])
    try:
        filename = sys.argv[1]
        with open(filename) as f:
            for line in f:
                s = line.split()
                try:
                    arr = np.append(arr, (float(s[-4]), float(s[-3]), float(s[-2]), float(s[-1])))
                except(ValueError, IndexError):
                    pass
        arr = np.reshape(arr, (int(len(arr)) / 4, 4))
        plt.plot(arr[:, 0], arr[:, 3], 'b-.')
        plt.plot(arr[:, 0], arr[:, 2], 'g-')
        plt.plot(arr[:, 0], arr[:, 1], 'r-')
        plt.grid(True)
        plt.xlabel('Path [mm]')
        plt.ylabel('Offset [mm]')
        plt.title(filename)
        plt.show()

    except(IndexError):
        print('Please provide filename.')


# --------------------
if __name__ == '__main__':
    main()
