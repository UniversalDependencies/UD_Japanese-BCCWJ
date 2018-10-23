# -*- coding: utf-8 -*-

"""

Converting CONLL file to blank data.

"""

import argparse



def _write_luw_map(luw_mapping, luw_mapping_file):
    """
        write luw mapping for `restore_word_unit_bccwj`
    """
    for pos_label, pos_num in luw_mapping.items():
        luw_mapping_file.write(
            u"{}\t{}\n".format(pos_label, pos_num).encode("utf-8")
        )


def replace_luw_word(conll_file, writer, luw_mapping):
    """
        replace blank file
    """
    for line in conll_file:
        items = line.decode("utf-8").rstrip("\r\n").split("\t")
        if len(items) == 10:
            lst = items[-1].split("|")
            for ppp, lll in enumerate(lst):
                kkk, vvv = lll.split("=")
                if kkk == "LUWPOS":
                    if vvv not in luw_mapping:
                        luw_mapping[vvv] = len(luw_mapping)
                    lst[ppp] = u"{}={}".format(kkk, luw_mapping[vvv])
            items[-1] = u"|".join(lst)
        writer.write(u"\t".join(items).encode("utf-8") + "\n")


def main():
    """
        main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_files", nargs="+", type=argparse.FileType("r"))
    parser.add_argument(
        "-l", "--luw-mapping-file", type=argparse.FileType("w"), default="./luw_mapping.txt"
    )
    parser.add_argument("-s", "--suffix", default=".sluw")
    args = parser.parse_args()
    luw_mapping = {}
    for conll in args.conll_files:
        with open(conll.name + args.suffix, "w") as writer:
            replace_luw_word(conll, writer, luw_mapping)
    _write_luw_map(luw_mapping, args.luw_mapping_file)


if __name__ == '__main__':
    main()
