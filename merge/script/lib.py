# -*- coding: utf-8 -*-

"""
    shared function
"""

import pickle as pkl
import itertools

COLCOUNT = 10
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(COLCOUNT)
CORE_SUW_COLUMN = [
    "サブコーパス名", "サンプルID", "文字開始位置", "文字終了位置", "連番",
    "出現形開始位置", "出現形終了位置", "固定長フラグ", "可変長フラグ", "文頭ラベル",
    "語彙表ID", "語彙素ID", "語彙素", "語彙素読み", "語彙素細分類",
    "語種", "品詞", "活用型", "活用形", "語形",
    "用法", "書字形", "書字形出現形", "原文文字列", "発音形出現形"
]
NUMBER_ORTH = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '０', '１', '２', '３', '４', '５', '６', '７', '８', '９',
}

def iterate_conll_and_bccwj(conll_st, bccwj_st):
    """
        iterate conll file and BCCWJ core file
    """
    nbccwj_pos = 0
    for sent_st in conll_st:
        # print(nbccwj_pos, sent_st[0], len(sent_st) - 2, len(bccwj_st[nbccwj_pos]))
        # print("\n".join(["\t".join(t) for t in bccwj_st[nbccwj_pos]]))
        if len(sent_st) - 2 == len(bccwj_st[nbccwj_pos]):
            yield sent_st, bccwj_st[nbccwj_pos]
            nbccwj_pos += 1
            continue
        nbbst = []
        while nbccwj_pos < len(bccwj_st) and len(sent_st) - 2 > len(nbbst):
            nbbst.extend(bccwj_st[nbccwj_pos])
            nbccwj_pos += 1
        # assert len(nbbst) == len(sent_st) - 2
        yield sent_st, nbbst


def separate_conll_sentence(conll_file, expand_sp=False):
    """
        separete conll by sentence
    """
    cstack = []
    for line in conll_file:
        if line == "":
            yield cstack
            cstack = []
            continue
        line = line.rstrip("\r\n").split("\t")
        cstack.append(line)
        if expand_sp and not line[0].startswith("#"):
            yesno = [
                s.split("=")[1] for s in line[MISC].split("|")
                if s.split("=")[0] == "SpaceAfter"
            ][0]
            if yesno == "Yes":
                cstack.append(["　"] + ["_" for _ in range(COLCOUNT-1)])


def sepacete_sentence_for_bccwj(bdoc, merge_num=True):
    """
        separate bccwj core data to each sentence.
    """
    nsent_lst, nsent, num_flag = [], [], False
    for rows in bdoc:
        if rows["文頭ラベル"] == "B":
            if len(nsent) > 0:
                nsent_lst.append(nsent)
            nsent = []
            num_flag = False
        if merge_num and (rows["品詞"] == "名詞-数詞" and rows["原文文字列"] in NUMBER_ORTH):
            if not num_flag:
                nsent.append([])
                num_flag = True
            nsent[-1].append(rows)
        elif merge_num and num_flag:
            assert rows["品詞"] != "名詞-数詞" or rows["原文文字列"] not in NUMBER_ORTH
            num_flag = False
            if rows["品詞"] != "空白":
                nsent.append([rows])
        else:
            if rows["品詞"] != "空白":
                nsent.append([rows])
    if len(nsent) > 0:
        nsent_lst.append(nsent)
    return nsent_lst


def conv_doc_id(conll):
    """
        convert doc ID
    """
    tid = conll.split(" ")[3].split("-")[0].split("_")
    if len(tid) < 3:
        return "_".join(tid)
    else:
        return "_".join(tid[1:])


def load_bccwj_core_file(base_file_name, load_pkl=False):
    """
        load bccwj core data
    """
    if load_pkl:
        return pkl.load(open(base_file_name + ".pkl", "rb"))
    base_file_map = {}
    with open(base_file_name, "r") as base_data:
        for rows in base_data:
            rows = dict(zip(CORE_SUW_COLUMN, rows.rstrip("\n").split("\t")))
            if rows["サンプルID"] not in base_file_map:
                base_file_map[rows["サンプルID"]] = []
            base_file_map[rows["サンプルID"]].append(rows)
    for sample_id in base_file_map:
        sent_bccwj = sepacete_sentence_for_bccwj(base_file_map[sample_id], merge_num=True)
        base_file_map[sample_id] = list(itertools.chain.from_iterable(sent_bccwj))
    return base_file_map


def separate_document(conll_file):
    """
        separete conll file by documents.
    """
    bstack, tid, prev_tid = [], None, None
    line = next(conll_file).rstrip("\n")
    try:
        while True:
            assert line.startswith("# sent_id =")
            tid = conv_doc_id(line)
            if prev_tid is not None and tid != prev_tid:
                yield prev_tid, bstack
                sent_cnt = 0
                bstack = []
            while line != "":
                bstack.append(line)
                line = next(conll_file).rstrip("\n")
            bstack.append(line)
            prev_tid = tid
            line = next(conll_file).rstrip("\n")
    except StopIteration:
        yield prev_tid, bstack


def is_spaceafter_yes(line):
    """
        SpaceAfter="Yes" extracted from line
    """
    if line[-1] == "_":
        return False
    for ddd in line[MISC].split("|"):
        kkk, vvv = ddd.split("=")
        if kkk == "SpaceAfter":
            return vvv == "Yes"
    raise ValueError
