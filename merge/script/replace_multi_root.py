# -*- coding: utf-8 -*-

"""
マルチルートを係り先を変更してシングルにする
プログラム
"""

import argparse
import json


def separate_document(conll_file):
    """
        文書ごとに区切る
    """
    bstack, tid, prev_tid = [], None, None
    line = conll_file.next().rstrip("\r\n").decode("utf-8")
    try:
        while True:
            assert line.startswith(u"# sent_id =")
            tid = line.split(" ")[3].split("-")[0]
            if prev_tid is not None and tid != prev_tid:
                yield bstack
                bstack = []
            while line != "":
                bstack.append(line)
                line = conll_file.next().rstrip("\r\n").decode("utf-8")
            bstack.append(line)
            prev_tid = tid
            line = conll_file.next().rstrip("\r\n").decode("utf-8")
    except StopIteration:
        yield bstack


def separate_sentence(conll_file):
    """
        文分割する
    """
    cstack = []
    for line in conll_file:
        if line == u"":
            yield cstack
            cstack = []
            continue
        cstack.append(line)


def _create_replaced_line_num(data, rm_lst):
    """
        restore below information to json file
            old_pos
               修正後のpos: 修正前のpos
            inserted_token
               修正前のpos: line
    """
    nmap, counter = {0: 0}, 1
    for line in data:
        num = int(line[0])
        if num in rm_lst:
            continue
        nmap[num] = counter
        counter += 1
    return nmap


def __remove_root(sent_id_line, data, sent_text_line):
    nsent_st = []
    lst = ["ROOT"] + [int(line[6]) for line in data]
    tree = {}
    for pos, dnum in enumerate(lst):
        if dnum == "ROOT":
            continue
        if dnum not in tree:
            tree[dnum] = set()
        tree[dnum].add(pos)
    numlst = sorted(tree[0])
    frmpos, true_root = numlst[:-1], numlst[-1]
    nsent_st.append(sent_id_line)
    nsent_st.append(sent_text_line)
    for line in data:
        num, dnum = int(line[0]), int(line[6])
        if num in frmpos:
            assert dnum == 0
            dnum = true_root
            line[7] = "dep"
        nsent_st.append(u"\t".join([unicode(num)] + line[1:6] + [unicode(dnum)] + line[7:]))
    return nsent_st


def _remove_root(sent_st):
    nsent_st = []
    sent_id_line = sent_st[0]
    sent_text_line = sent_st[1]
    data = [line.rstrip("\n").split("\t") for line in sent_st[2:]]
    cnum = sum([int(int(d[6]) == 0) for d in data])
    #if cnum > 1:
    #    print cnum, sent_id_line.split(" ")[3]
    if cnum == 1:
        return sent_st
    elif cnum == 0:
        assert ValueError, "{} must be rather one.".format(cnum)
    else:
        nsent_st = __remove_root(sent_id_line, data, sent_text_line)
    return nsent_st


def remove_root_from_sentence(conll_file, writer):
    """
        fill word by bccwj file
    """
    for cnl in separate_document(conll_file):
        assert cnl[0].startswith("# sent_id =")
        for sent_st in separate_sentence(cnl):
            sent = _remove_root(sent_st)
            for sss in sent:
                writer.write(sss.encode("utf-8") + "\n")
            writer.write("\n")


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_file", type=argparse.FileType("r"))
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    args = parser.parse_args()
    remove_root_from_sentence(args.conll_file, args.writer)


if __name__ == '__main__':
    _main()
