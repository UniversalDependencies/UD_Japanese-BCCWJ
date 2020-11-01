# -*- coding: utf-8 -*-

"""
restore token from BCCWJ core file.
"""

import argparse
import string
import re
import pickle as pkl

from lib import (
    separate_document, load_bccwj_core_file, conv_doc_id,
    sepacete_sentence_for_bccwj, separate_conll_sentence,
    is_spaceafter_yes, iterate_conll_and_bccwj, FORM, ID, MISC, LEMMA, XPOS
)

RE_PROP_MATH = re.compile(".*固有名詞.*")
RE_ASCII_MATH = re.compile('^[' + string.printable + ']+$')

UNIDIC_ORIGIN_CONV = {
    "ず": "ぬ",
    '為る': 'する',
    '居る': 'いる',
    "出来る": "できる",
    "有る": "ある",
    "無い": "ない",
    "成る": "なる",
    "仕舞う": "しまう",
    "レる": "れる",
    "在る": "ある",
    "如し": "ごとし",
    "頂く": "いただく",
    "良い": "よい",
    "頂ける": "いただく",
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
}

def get_origin(bccwj):
    """
        convert UD LEMMA from Unidic lemma
    """
    if RE_PROP_MATH.match(bccwj["品詞"]):
        return bccwj["原文文字列"]
    if RE_ASCII_MATH.match(bccwj["原文文字列"]):
        return bccwj["原文文字列"]
    if bccwj["語彙素"] == "":
        return "_"
    if bccwj["語彙素"] == "です":
        return "だ"
    if bccwj["語彙素"] in UNIDIC_ORIGIN_CONV:
        return UNIDIC_ORIGIN_CONV[bccwj["語彙素"]]
    return bccwj["語彙素"]


def _convert_misc(conll, misc_data):
    """
        convert MISC Filed
    """
    nfes = []
    for item in conll[MISC].split("|"):
        key, value = item.split("=")
        if key == "SpaceAfter":
            nfes.append(key + "=" + str(value))
            continue
        if misc_data["label_bl_to_org"][key] in ["BunsetuPositionType", "LUWPOS"]:
            value = misc_data["cont_bl_to_org"][misc_data["label_bl_to_org"][key]][int(value)]
        if key in ["BPT", "LPOS", "BBIL", "LBIL"]:
            key = misc_data["label_bl_to_org"][key]
        nfes.append(key + "=" + str(value))
    return nfes


def _divide_sentence(cnl, tid, bccwj_conll_mapping):
    sentence_list, sent = [], []
    for cpos, item in enumerate(cnl):
        if cpos not in bccwj_conll_mapping[tid]:
            print(item)
            assert item.startswith("# ") or item == ""
            if item == "":
                sentence_list.append(sent)
                sent = []
            else:
                sent.append((item, None))
        else:
            # bccwj_conll_mapping[tid][cpos] -> [bpos, num_flag, num_pos]
            sent.append((item, bccwj_conll_mapping[tid][cpos]))
    assert sent == []
    return sentence_list


def _expand_sentence(sent, bccwj_data):
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


def fill_blank_files(conll_file, base_data, bccwj_conll_mapping, misc_mapping, writer):
    """
        fill word by bccwj file
    """
    for tid, cnl in separate_document(conll_file):
        assert cnl[0].startswith("# sent_id =")
        assert tid in base_data, tid
        bccwj_data = base_data[tid]
        sentence_list = _divide_sentence(cnl, tid, bccwj_conll_mapping)
        for sent in sentence_list:
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
                    ]), '名詞-数詞'
                else:
                    assert len(bccwj_info) == 1
                    cll[FORM], cll[LEMMA], cll[XPOS] = bccwj_info[0]["原文文字列"], get_origin(bccwj_info[0]), bccwj_info[0]["品詞"]
                    if cll[FORM] == "目　　　　　　　　次":
                        cll[FORM] = "目　次"
                cll[FORM] = cll[FORM].strip("　")
                writer.write("\t".join(cll[ID:MISC] + ["|".join(misc_info)]) + "\n")
            writer.write("\n")


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("conll_file", type=argparse.FileType("r"))
    parser.add_argument("bccwj_file_name", help="BCCWJ core file (core_SUW.txt)")
    parser.add_argument("bccwj_conll_mapping", type=argparse.FileType("rb"))
    parser.add_argument("-w", "--writer", type=argparse.FileType("w"), default="-")
    parser.add_argument(
        "-m", "--misc-file", type=argparse.FileType("rb"), default="./misc_mapping.pkl"
    )
    args = parser.parse_args()
    base_data = load_bccwj_core_file(args.bccwj_file_name, load_pkl=True)
    misc_mapping = pkl.load(args.misc_file)
    bccwj_conll_mapping = pkl.load(args.bccwj_conll_mapping)
    fill_blank_files(
        args.conll_file, base_data, bccwj_conll_mapping, misc_mapping, args.writer
    )


if __name__ == '__main__':
    _main()
