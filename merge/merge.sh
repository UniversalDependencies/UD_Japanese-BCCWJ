#!/bin/sh

usage () {
    echo "Usage: $0 [-f] -c CORE_FILE"
    echo "-c: set the file of BCCWJ core file (core_SUW.txt, requirement)"
    echo "-f: if you want to get originl full text."
    exit 1
}

BASE_DIR=$(cd $(dirname $0); pwd)

PYTHON=python
BASE_PROG=$BASE_DIR/script/restore_word_unit_bccwj.py
BASE_PROG2=$BASE_DIR/script/replace_multi_root.py
CORE_FILE=""
FULL_FLAG=false

while getopts c:hf OPT
do
    case $OPT in
	c)  CORE_FILE=$OPTARG
	    ;;
	f)  FULL_FLAG=true
	    ;;
	h)  usage
	    ;;
	*) usage
	    ;;
    esac
done
shift `expr $OPTIND - 1`
TARGET_FILES="ja_bccwj-ud-train.conllu ja_bccwj-ud-dev.conllu ja_bccwj-ud-test.conllu"

if [ "$CORE_FILE" = "" ]; then
    echo "No argments: $CORE_FILE"
    usage
fi
if [ ! -f $CORE_FILE ]; then
    echo "Not found: $CORE_FILE"
    usage
fi

for FILE in $TARGET_FILES; do
    if $FULL_FLAG; then
        echo $PYTHON $BASE_PROG ./$FILE $BASE_DIR/script/$FILE.diff $CORE_FILE -w ./$FILE.mr.word -f
        $PYTHON $BASE_PROG ./$FILE $BASE_DIR/script/$FILE.diff $CORE_FILE -w ./$FILE.mr.word -f
    else
        echo $PYTHON $BASE_PROG ./$FILE $BASE_DIR/script/$FILE.diff $CORE_FILE -w ./$FILE.word
        $PYTHON $BASE_PROG ./$FILE $BASE_DIR/script/$FILE.diff $CORE_FILE -w ./$FILE.word
    fi
done

if $FULL_FLAG; then
    for FILE in $TARGET_FILES; do
        $PYTHON $BASE_PROG2 ./$FILE.mr.word -w ./$FILE.word
    done
fi
