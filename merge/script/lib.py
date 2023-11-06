# -*- coding: utf-8 -*-

"""
    shared function
"""

import itertools
import pickle as pkl
from typing import Iterable, Optional, TextIO

COLCOUNT = 10
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(COLCOUNT)
CORE_SUW_COLUMN = [
    "サブコーパス名", "サンプルID", "文字開始位置", "文字終了位置", "連番",
    "出現形開始位置", "出現形終了位置", "固定長フラグ", "可変長フラグ", "文頭ラベル",
    "語彙表ID", "語彙素ID", "語彙素", "語彙素読み", "語彙素細分類",
    "語種", "品詞", "活用型", "活用形", "語形",
    "用法", "書字形", "書字形出現形", "原文文字列", "発音形出現形"
]
CORE_LUW_COLUMN = [
    "サブコーパス名", "サンプルID",
    "出現形開始位置", "出現形終了位置", "文節",
    "短長相違フラグ", "固定長フラグ", "可変長フラグ",
    "語彙素", "語彙素読み", "語種", "品詞", "活用型", "活用形", "語形",
    "書字形", "書字形出現形", "原文文字列", "発音形出現形", "連番",
    "文字開始位置", "文字終了位置", "文頭ラベル"
]
NUMBER_ORTH = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '０', '１', '２', '３', '４', '５', '６', '７', '８', '９',
}


def separate_conll_sentence(conll_file: TextIO, expand_sp: bool=False) -> Iterable[list[list[str]]]:
    """
        separete conll by sentence
    """
    cstack: list[list[str]] = []
    for line in conll_file:
        if line == "":
            yield cstack
            cstack = []
            continue
        items = line.rstrip("\r\n").split("\t")
        cstack.append(items)
        if expand_sp and not items[0].startswith("#"):
            yesno = [
                s.split("=")[1] for s in items[MISC].split("|")
                if s.split("=")[0] == "SpacesAfter"
            ][0]
            if yesno == "Yes":
                cstack.append(["　"] + ["_" for _ in range(COLCOUNT-1)])


def sepacete_sentence_for_bccwj(
    bdoc: list[dict[str, str]], merge_num: bool=True
) -> list[list[list[dict[str, str]]]]:
    """
        separate bccwj core data to each sentence.
    """
    nsent_lst: list[list[list[dict[str, str]]]] = []
    nsent: list[list[dict[str, str]]] = []
    num_flag: bool = False
    for rows in bdoc:
        if rows["文頭ラベル"] == "B":
            if len(nsent) > 0:
                nsent_lst.append(nsent)
            nsent = []
            num_flag = False
        if merge_num and (rows["品詞"] == "名詞-数詞" and all([r in NUMBER_ORTH for r in rows["原文文字列"]])):
            if not num_flag:
                nsent.append([])
                num_flag = True
            nsent[-1].append(rows)
        elif merge_num and num_flag:
            assert rows["品詞"] != "名詞-数詞" or not all([r in NUMBER_ORTH for r in rows["原文文字列"]])
            num_flag = False
            if rows["品詞"] != "空白":
                nsent.append([rows])
        else:
            if rows["品詞"] != "空白":
                nsent.append([rows])
    if len(nsent) > 0:
        nsent_lst.append(nsent)
    return nsent_lst


def conv_doc_id(conll: str) -> str:
    """
        convert doc ID
    """
    tid = conll.split(" ")[3].split("-")[0].split("_")
    if len(tid) < 3:
        return "_".join(tid)
    return "_".join(tid[1:])


def load_bccwj_core_file(
    base_file_name: str, unit: str="suw", load_pkl: bool=False
) -> dict[str, list[list[dict[str, str]]]]:
    """
        load bccwj core data
    """
    if load_pkl:
        with open(base_file_name + ".pkl", "rb") as rdr:
            ldata: dict[str, list[list[dict[str, str]]]] = pkl.load(rdr)
            return ldata
    assert unit in ["suw", "luw"]
    nbase_file_map: dict[str, list[dict[str, str]]] = {}
    base_file_map: dict[str, list[list[dict[str, str]]]] = {}
    with open(base_file_name, "r", encoding="utf-8") as base_data:
        for line in base_data:
            rows: dict[str, str] = dict(
                zip({"suw": CORE_SUW_COLUMN,
                     "luw": CORE_LUW_COLUMN}[unit], line.rstrip("\n").split("\t"))
            )
            if rows["サンプルID"] not in nbase_file_map:
                nbase_file_map[rows["サンプルID"]] = []
            nbase_file_map[rows["サンプルID"]].append(rows)
    for sample_id, nbase_data in nbase_file_map.items():
        sent_bccwj = sepacete_sentence_for_bccwj(nbase_data, merge_num=True)
        base_file_map[sample_id] = list(itertools.chain.from_iterable(sent_bccwj))
    return base_file_map


def separate_document(conll_file: TextIO) -> Iterable[tuple[Optional[str], list[str]]]:
    """
        separete conll file by documents.
    """
    bstack: list[str] = []
    tid, prev_tid = None, None
    try:
        line = next(conll_file).rstrip("\n")
        while True:
            assert line.startswith("# sent_id =")
            tid = conv_doc_id(line)
            if prev_tid is not None and tid != prev_tid:
                yield prev_tid, bstack
                bstack = []
            while line != "":
                bstack.append(line)
                line = next(conll_file).rstrip("\n")
            bstack.append(line)
            prev_tid = tid
            line = next(conll_file).rstrip("\n")
    except StopIteration:
        yield prev_tid, bstack


def is_spaceafter_yes(line: list[str]) -> bool:
    """
        SpaceAfter="Yes" extracted from line
    """
    if line[-1] == "_":
        return False
    for ddd in line[MISC].split("|"):
        kkk, vvv = ddd.split("=")
        if kkk == "SpacesAfter":
            return vvv == "Yes"
        if kkk == "SpaceAfter":
            return vvv != "No"
    return True
