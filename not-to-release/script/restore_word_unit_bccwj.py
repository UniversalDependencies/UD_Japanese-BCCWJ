# -*- coding: utf-8 -*-

"""
restore token from BCCWJ core file.
"""

import argparse
import json


def separate_document(conll_file):
    """
        separete by documents.
    """
    bstack, tid, prev_tid = [], None, None
    rows = conll_file.next().rstrip("\r\n").decode("utf-8")
    try:
        while True:
            assert rows.startswith(u"# sent_id =")
            tid = rows.split(" ")[3].split("-")[0]
            if prev_tid is not None and tid != prev_tid:
                yield bstack
                bstack = []
            while rows != "":
                bstack.append(rows)
                rows = conll_file.next().rstrip("\r\n").decode("utf-8")
            bstack.append(rows)
            prev_tid = tid
            rows = conll_file.next().rstrip("\r\n").decode("utf-8")
    except StopIteration:
        yield bstack


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


def _pre_convert(txt):
    txt = txt.replace(u"　", u"[JSP]")
    return txt if txt != "" else "_"


def _conv_doc_id(rows):
    tid = rows.split(" ")[3]
    tid = tid.split("-")[0].split("_")
    if len(tid) < 3:
        return u"_".join(tid)
    else:
        return u"_".join(tid[1:])


def fill_blank_files(conll_file, base_file, restore_data, is_full, writer):
    """
        fill word by bccwj file
    """
    for cnl in separate_document(conll_file):
        assert cnl[0].startswith("# sent_id =")
        tid = _conv_doc_id(cnl[0])
        assert tid in base_file, tid
        bdoc = iter(base_file[tid])
        for rdata, sent_st in separate_sentence(cnl, restore_data):
            if rdata is None:
                sent = [(sss.split("\t"), bdoc.next(), False) for sss in sent_st[2:]]
            else:
                osent = ["ROOT"] + [sss.split("\t") for sss in sent_st[2:]]
                sent = []
                nlst = sorted([
                    int(n) for n in rdata["old_pos"].keys() + rdata["inserted_token"].keys()
                ])
                for num in nlst:
                    num = str(num)
                    if num in rdata["old_pos"]:
                        if num == "0":
                            continue
                        sss = osent[rdata["old_pos"][num]]
                        sent.append((sss, bdoc.next(), False))
                    elif num in rdata["inserted_token"]:
                        sent.append((rdata["inserted_token"][num].split("\t"), bdoc.next(), True))
                    else:
                        raise ValueError, "the num is not found. {}:{}".format(tid, num)
            writer.write(sent_st[0].encode("utf-8") + "\n")
            writer.write(u"# text = {}".format(
                u"".join([_pre_convert(s[1][-2]) for s in sent if is_full or not s[2]])
            ).encode("utf-8") + "\n")
            nmap = {}
            if is_full and rdata is not None:
                for pos, sss in enumerate(sent):
                    if not sss[2]:
                        nmap[int(sss[0][0])] = pos + 1
            for rows, the_word, skipped in sent:
                if not is_full and skipped:
                    continue
                rows[1] = _pre_convert(the_word[-2])
                rows[2] = _pre_convert(the_word[12])
                rows[4] = the_word[16]
                nfes = []
                for item in rows[9].split("|"):
                    if item.startswith("JPYomi"):
                        item = u"JPYomi={}".format(
                            the_word[13] if the_word[13] != "" else "_"
                        )
                    nfes.append(item)
                if is_full and rdata is not None and not skipped:
                    rnum, dnum = int(rows[0]), int(rows[6])
                    if rnum in nmap:
                        rnum = nmap[rnum]
                    if dnum in nmap:
                        dnum = nmap[dnum]
                    writer.write(
                        u"\t".join(
                            [
                                unicode(rnum)
                            ] + rows[1:6] + [unicode(dnum)] + rows[7:9] + [u"|".join(nfes)
                        ]).encode("utf-8") + "\n"
                    )
                else:
                    writer.write(u"\t".join(rows[:9] + [u"|".join(nfes)]).encode("utf-8") + "\n")
            writer.write("\n")


def _load_base_file(base_file):
    base_file_map = {}
    for rows in base_file:
        rows = rows.rstrip("\n").decode("utf-8").split("\t")
        if rows[1] not in base_file_map:
            base_file_map[rows[1]] = []
        base_file_map[rows[1]].append(rows)
    return base_file_map


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_file", type=argparse.FileType("r"))
    parser.add_argument("restore_file", type=argparse.FileType("r"))
    parser.add_argument(
        "bccwj_file", type=argparse.FileType("r"), help="BCCWJ core file (core_SUW.txt)"
    )
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    parser.add_argument(
        "-f", "--full-text", action="store_true",
        help="expansion text without considering multi-root"
    )
    args = parser.parse_args()
    restore_data = json.load(args.restore_file)
    base_file = _load_base_file(args.bccwj_file)
    fill_blank_files(args.conll_file, base_file, restore_data, args.full_text, args.writer)


if __name__ == '__main__':
    _main()
