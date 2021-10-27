# -*- coding: utf-8 -*-

"""

save CORE SUW data to pickle file

"""

import argparse
import pickle as pkl
from lib import load_bccwj_core_file


def main():
    """
        main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("bccwj_file_name")
    parser.add_argument("unit", choices=["suw", "luw"])
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    args = parser.parse_args()
    base_data = load_bccwj_core_file(args.bccwj_file_name, unit=args.unit, load_pkl=False)
    with open(args.bccwj_file_name + ".pkl", "wb") as wrt:
        pkl.dump(base_data, wrt, protocol=4)


if __name__ == '__main__':
    main()
