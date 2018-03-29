# -*- coding: utf-8 -*-

"""
restore token from BCCWJ core file.
"""

import argparse


def separate_document(conll_file):
    """
        separete by documents.
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
       separate by sentence
    """
    cstack = []
    for line in conll_file:
        if line == u"":
            yield cstack
            cstack = []
            continue
        cstack.append(line)


def _pre_convert(txt):
    txt = txt.replace(u"　", u"[JSP]")
    return txt if txt != "" else "_"


def _conv_doc_id(line):
    tid = line.split(" ")[3]
    tid = tid.split("-")[0].split("_")
    if len(tid) < 3:
        return u"_".join(tid)
    else:
        return u"_".join(tid[1:])


def fill_blank_files(conll_file, base_file, writer):
    """
        fill word by bccwj file
    """
    for cnl in separate_document(conll_file):
        assert cnl[0].startswith("# sent_id =")
        tid = _conv_doc_id(cnl[0])
        assert tid in base_file, tid
        bdoc = iter(base_file[tid])
        for sent_st in separate_sentence(cnl):
            sent = [(ss.split("\t"), bdoc.next()) for ss in sent_st[2:]]
            writer.write(sent_st[0].encode("utf-8") + "\n")
            writer.write(u"# text = {}".format(
                u"".join([_pre_convert(s[1][-2]) for s in sent])
            ).encode("utf-8") + "\n")
            for line, the_word in sent:
                line[1] = _pre_convert(the_word[-2])
                line[2] = _pre_convert(the_word[12])
                line[4] = the_word[16]
                nfes = []
                for item in line[9].split("|"):
                    if item.startswith("JPYomi"):
                        item = u"JPYomi={}".format(
                            the_word[13] if the_word[13] != "" else "_"
                        )
                    nfes.append(item)
                nfes = u"|".join(nfes)
                writer.write(u"\t".join(line[:9] + [nfes]).encode("utf-8") + "\n")
            writer.write("\n")


def _load_base_file(base_file):
    base_file_map = {}
    for line in base_file:
        line = line.rstrip("\n").decode("utf-8").split("\t")
        if line[1] not in base_file_map:
            base_file_map[line[1]] = []
        base_file_map[line[1]].append(line)
    return base_file_map


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_file", type=argparse.FileType("r"))
    parser.add_argument("bccwj_file", type=argparse.FileType("r"), help="BCCWJ core file (core_SUW.txt)")
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    args = parser.parse_args()
    base_file = _load_base_file(args.bccwj_file)
    fill_blank_files(args.conll_file, base_file, args.writer)


if __name__ == '__main__':
    _main()
