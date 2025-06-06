# -*- coding: utf-8 -*-

"""
Restore token from BCCWJ core file.
"""

import argparse
import pickle as pkl
import re
import string
from functools import partial
from typing import Optional, TextIO

from lib import (FORM, ID, LEMMA, MISC, XPOS, is_spaceafter_yes,
                 load_bccwj_core_file, separate_document)

RE_PROP_MATH = re.compile(".*固有名詞.*")
RE_ASCII_MATH = re.compile('^[' + string.printable + ']+$')

UNIDIC_ORIGIN_CONV = {
    "ず": "ぬ",
    "為る": "する",
    "居る": "いる",
    "出来る": "できる",
    "有る": "ある",
    "無い": "ない",
    "なかっ": "ない",
    "なく": "ない",
    "成る": "なる",
    "仕舞う": "しまう",
    "レる": "れる",
    "在る": "ある",
    "如し": "ごとし",
    "頂く": "いただく",
    "良い": "よい",
    "頂ける": "いただける",
    "貰う": "もらう",
    "下さる": "くださる",
    "欲しい": "ほしい",
    "過ぎる": "すぎる",
    "タ": "た",
    "様": "よう",
    "見る": "みる",
    "得る": "える",
    "チャウ": "ちゃう",
    "知れる": "しれる",
    "貰える": "もらえる",
    "致す": "いたす",
    "為さる": "なさる"
}

def get_origin(bccwj: dict[str, str]) -> str:
    """
        Convert UD LEMMA from Unidic lemma
    """
    if bccwj["語彙素"] == "":
        return "_"
    if bccwj["品詞"].startswith("名詞-固有名詞"):
        return bccwj["原文文字列"]
    return bccwj["語彙素"]


def _convert_misc(conll, misc_data):
    """
        convert MISC Filed
    """
    nfes = []
    for item in conll[MISC].split("|"):
        key, value = item.split("=")
        if key in ("SpaceAfter", "SpacesAfter"):
            nfes.append(key + "=" + str(value))
            continue
        if misc_data["label_bl_to_org"][key] in ["BunsetuPositionType", "LUWPOS", "UnidicInfo"]:
            value = misc_data["cont_bl_to_org"][misc_data["label_bl_to_org"][key]][int(value)]
        if key in ["BPT", "LPOS", "BBIL", "LBIL", "UI", "PUDL"]:
            key = misc_data["label_bl_to_org"][key]
        nfes.append(key + "=" + str(value))
    return nfes


def _divide_sentence(cnl, tid, bccwj_conll_mapping):
    sentence_list: list = []
    sent: list = []
    for cpos, item in enumerate(cnl):
        if cpos not in bccwj_conll_mapping[tid]:
            assert item.startswith("# ") or item == ""
            if item == "":
                sentence_list.append(sent)
                sent = []
            else:
                sent.append((item, None))
        else:
            # bccwj_conll_mapping[tid][cpos] -> [bpos, num_flag, num_pos]
            sent.append((item, bccwj_conll_mapping[tid][cpos]))
    assert not sent
    return sentence_list


def _expand_sentence(sent, bccwj_data) -> str:
    sent_s = ""
    for conll, bccwj in sent[2:]:
        bpos, num_flag, num_pos = bccwj
        if num_flag:
            sent_s += "".join([bccwj_data[bpos][p]["原文文字列"] for p in num_pos])
        else:
            sent_s += "".join([
                b["原文文字列"]  if b["原文文字列"] != "目　　　　　　　　次" else "目　次"
                for b in bccwj_data[bpos]
            ])
        if is_spaceafter_yes(conll.split("\t")):
            sent_s += "　"
    return "# text = {}\n".format(sent_s.strip("　"))


def fill_blank_files(
    conll_file, base_data, bccwj_conll_mapping,
    misc_mapping, error_files, writer
) -> None:
    """
        fill word by bccwj file
    """
    error_keys = [(e[0], e[1].rstrip()) for e in error_files.keys()]
    for tid, cnl in separate_document(iter(conll_file)):
        assert cnl[0].startswith("# sent_id =")
        assert tid in base_data, tid
        bccwj_data = base_data[tid]
        sentence_list = _divide_sentence(cnl, tid, bccwj_conll_mapping)
        for sent in sentence_list:
            if tuple(sent[0][0].split(" ")[-1].split("-")) in error_keys:
                continue
            writer.write(sent[0][0] + "\n")
            writer.write(_expand_sentence(sent, bccwj_data))
            for conll, bccwj in sent[2:]:
                cll = conll.split("\t")
                bpos, num_flag, num_pos = bccwj
                misc_info = _convert_misc(cll, misc_mapping)
                bccwj_info = bccwj_data[bpos]
                if num_flag:
                    cll[FORM], cll[LEMMA], cll[XPOS] = "".join([
                        bccwj_info[p]["原文文字列"] for p in num_pos
                    ]), "".join([
                        get_origin(bccwj_info[p]) for p in num_pos
                    ]), "名詞-数詞"
                else:
                    assert len(bccwj_info) == 1
                    cll[FORM], cll[LEMMA], cll[XPOS] = (
                        bccwj_info[0]["原文文字列"],
                        get_origin(bccwj_info[0]),
                        (bccwj_info[0]["品詞"] + "-" + bccwj_info[0]["活用型"]\
                            if bccwj_info[0]["活用型"] != "" else bccwj_info[0]["品詞"])
                    )
                    if cll[FORM] == "目　　　　　　　　次":
                        cll[FORM] = "目　次"
                cll[FORM] = cll[FORM].strip("　")
                writer.write("\t".join(cll[ID:MISC] + ["|".join(misc_info)]) + "\n")
            writer.write("\n")


def _separete_conll_to_sent(conll: TextIO):
    sent_list: list = []
    sent: list = []
    for line in conll:
        if line == "\n":
            sent_list.append(sent)
            sent = []
        else:
            sent.append(line)
    return sent_list


def _sentid(lst, order: Optional[dict]=None) -> tuple:
    if order is None:
        order = {}
    if len(lst) == 1:
        sid, num = lst[0].rstrip("\n"), 1
    else:
        sid, num = lst
    if len(sid.split("_")) > 2:
        sid = "_".join(sid.split("_")[1:3])
    else:
        sid = "_".join(sid.split("_")[0:2])
    return order[sid], int(num)


def merge_remove_sentence(conll_file, error_sent: dict, order_data: dict):
    """ Merge remove sentence """
    conll_sent_list = _separete_conll_to_sent(conll_file)
    conlls = {}
    for snt in conll_sent_list:
        sent_id = tuple(snt[0].split(" ")[-1].split("-"))
        conlls[sent_id] = snt
    result = []
    sids = list(conlls.keys()) + list(error_sent.keys())
    for sid in sorted(sids, key=partial(_sentid, order=order_data)):
        if sid in error_sent:
            for ccc in error_sent[sid]:
                result.append(ccc)
        else:
            for ccc in conlls[sid]:
                result.append(ccc)
        result.append("\n")
    return result


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_file", type=argparse.FileType("r"))
    parser.add_argument("bccwj_file_name", help="BCCWJ core file (core_*.txt)")
    parser.add_argument("bccwj_conll_mapping", type=argparse.FileType("rb"))
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    parser.add_argument(
        "-m", "--misc-file", type=argparse.FileType("rb"), default="./merged/misc_mapping.pkl"
    )
    args = parser.parse_args()
    base_data = load_bccwj_core_file(args.bccwj_file_name, load_pkl=True)
    misc_mapping = pkl.load(args.misc_file)
    bccwj_conll_mapping, error_files, order_data = pkl.load(args.bccwj_conll_mapping)
    conll_file = merge_remove_sentence(args.conll_file, error_files, order_data)
    fill_blank_files(
        conll_file, base_data, bccwj_conll_mapping, misc_mapping, error_files, args.writer
    )


if __name__ == '__main__':
    _main()
