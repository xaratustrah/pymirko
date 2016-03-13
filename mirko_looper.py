#!/usr/bin/env python
"""
MIRKO Looper script

2016 Xaratustrah

"""

import sys, os
from subprocess import call

TEMP_FILENAME = 'temp.mak'
MIRKO = 'java -jar ../../jMirko/dist/jMirko.jar'
PLACEHOLDER = 'NUMBERPLACEHOLDER'


def main():
    try:
        with open(sys.argv[1]) as f:
            a = f.read()

        for i in range(5):
            with open(TEMP_FILENAME, 'w') as f:
                f.write(a.replace(PLACEHOLDER, '{}'.format(i)))
            cmd = MIRKO.split()
            cmd.append(TEMP_FILENAME)
            print(cmd)
            # b = call(cmd)

            os.remove(TEMP_FILENAME)

    except(IndexError):
        print('Please provide filename.')


# --------------------
if __name__ == '__main__':
    main()
