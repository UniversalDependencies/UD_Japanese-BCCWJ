# -*- coding: utf-8 -*-

"""
    shared function
"""


def iterate_conll_and_bccwj(conll_st, bccwj_st):
    """
        iterate conll file and BCCWJ core file
    """
    nbccwj_pos = 0
    for sent_st in conll_st:
        assert len(sent_st) - 2 >= len(bccwj_st[nbccwj_pos])
        if len(sent_st) - 2 == len(bccwj_st[nbccwj_pos]):
            yield sent_st, bccwj_st[nbccwj_pos]
            nbccwj_pos += 1
            continue
        nbbst = []
        while len(sent_st) - 2 > len(nbbst):
            nbbst.extend(bccwj_st[nbccwj_pos])
            nbccwj_pos += 1
        # print len(nbbst), len(sent_st) - 2
        #for aaa, bbb in zip(nbbst, sent_st[2:]):
        #    print bbb, aaa[-2]
        assert len(nbbst) == len(sent_st) - 2
        yield sent_st, nbbst


def separate_conll_sentence(conll_file):
    """
        separete conll by sentence
    """
    cstack = []
    for line in conll_file:
        if line == u"":
            yield cstack
            cstack = []
            continue
        cstack.append(line.rstrip("\r\n"))


def sepacete_sentence_for_bccwj(bdoc):
    """
        separate bccwj core data to each sentence.
    """
    nsent_lst, nsent = [], []
    for bbb in bdoc:
        if bbb[9] == "B":
            if len(nsent) > 0:
                nsent_lst.append(nsent)
            nsent = []
        if bbb[16] != u"空白":
            nsent.append(bbb)
    if len(nsent) > 0:
        nsent_lst.append(nsent)
    return nsent_lst


def conv_doc_id(rows):
    """
        convert doc ID
    """
    tid = rows.split(" ")[3]
    tid = tid.split("-")[0].split("_")
    if len(tid) < 3:
        return u"_".join(tid)
    else:
        return u"_".join(tid[1:])


def load_bccwj_core_file(base_file):
    """
        load bccwj core data
    """
    base_file_map = {}
    for rows in base_file:
        rows = rows.rstrip("\n").decode("utf-8").split("\t")
        if rows[1] not in base_file_map:
            base_file_map[rows[1]] = []
        base_file_map[rows[1]].append(rows)
    return base_file_map


def separate_document(conll_file):
    """
        separete conll file by documents.
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


def is_spaceafter_yes(line):
    """
        SpaceAfter="Yes" extracted from line
    """
    # print line
    for ddd in line[-1].split(u"|"):
        kkk, vvv = ddd.split("=")
        if kkk == "SpaceAfter":
            return vvv == "Yes"
    raise ValueError
