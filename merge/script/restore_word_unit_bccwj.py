# -*- coding: utf-8 -*-

"""
restore token from BCCWJ core file.
"""

import argparse


from lib import (
    separate_document, load_bccwj_core_file, conv_doc_id,
    sepacete_sentence_for_bccwj, separate_conll_sentence,
    is_spaceafter_yes, iterate_conll_and_bccwj
)


def separate_sentence(conll_file, restore_data):
    """
       separate by sentence
    """
    cstack, rdata = [], None
    for rows in conll_file:
        if rows == u"":
            yield rdata, cstack
            cstack, rdata = [], None
            continue
        elif rows.startswith(u"# sent_id"):
            sent_id = rows.split(" ")[3]
            if sent_id in restore_data:
                rdata = restore_data[sent_id]
        cstack.append(rows)


def _load_luw_map(luw_mapping_file):
    """
        write luw mapping for `restore_word_unit_bccwj`
    """
    luw_mapping = {}
    for line in luw_mapping_file:
        line = line.decode("utf-8").rstrip("\n").split("\t")
        pos_label, pos_num = line[0], int(line[1])
        luw_mapping[pos_num] = pos_label
    return luw_mapping


def _pre_convert(txt):
    return txt.strip(u"　") if txt != "" else "_"


def fill_blank_files(conll_file, base_file, writer, luw_mapping):
    """
        fill word by bccwj file
    """
    for cnl in separate_document(conll_file):
        assert cnl[0].startswith("# sent_id =")
        tid = conv_doc_id(cnl[0])
        assert tid in base_file, tid
        conll_st = list(separate_conll_sentence(cnl))
        bccwcj_st = sepacete_sentence_for_bccwj(iter(base_file[tid]))
        for sent_st, bbb_st in iterate_conll_and_bccwj(conll_st, bccwcj_st):
            sent = [(a.split("\t"), b) for a, b in zip(sent_st[2:], bbb_st)]
            writer.write(sent_st[0].encode("utf-8") + "\n")
            writer.write(
                u"# text = {}".format(u"".join([
                    w[1][-2] + u"　" if is_spaceafter_yes(w[0]) else w[1][-2] for w in sent
                ]).strip(u"　")).encode("utf-8") + "\n"
            )
            for rows, the_word in sent:
                rows[1] = _pre_convert(the_word[-2])
                rows[2] = _pre_convert(the_word[12])
                rows[4] = the_word[16]
                nfes = []
                for item in rows[9].split("|"):
                    if item.startswith("JPYomi"):
                        item = u"JPYomi={}".format(
                            the_word[13] if the_word[13] != "" else "_"
                        )
                    if item.startswith("LUWPOS"):
                        luw_pos_num = int(item.split("=")[1])
                        item = u"LUWPOS={}".format(luw_mapping[luw_pos_num])
                    nfes.append(item)
                writer.write(u"\t".join(rows[:9] + [u"|".join(nfes)]).encode("utf-8") + "\n")
            writer.write("\n")


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_file", type=argparse.FileType("r"))
    parser.add_argument(
        "bccwj_file", type=argparse.FileType("r"), help="BCCWJ core file (core_SUW.txt)"
    )
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    parser.add_argument(
        "-f", "--full-text", action="store_true",
        help="expansion text without considering multi-root"
    )
    parser.add_argument(
        "-l", "--luw-mapping-file", type=argparse.FileType("r"),
        default="./luw_mapping.txt"
    )
    args = parser.parse_args()
    base_file = load_bccwj_core_file(args.bccwj_file)
    luw_mapping = _load_luw_map(args.luw_mapping_file)
    fill_blank_files(
        args.conll_file, base_file, args.writer, luw_mapping
    )


if __name__ == '__main__':
    _main()
