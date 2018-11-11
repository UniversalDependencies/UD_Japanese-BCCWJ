#!/bin/sh

usage () {
    echo "Usage: $0 -c CORE_FILE"
    echo "-c: set the file of BCCWJ core file (core_SUW.txt, requirement)"
    exit 1
}

BASE_DIR=$(cd $(dirname $0); pwd)

PYTHON=python
BASE_PROG=$BASE_DIR/script/restore_word_unit_bccwj.py
CORE_FILE=""
FULL_FLAG=false

while getopts c:hf OPT
do
    case $OPT in
	c)  CORE_FILE=$OPTARG
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
    echo $PYTHON $BASE_PROG ./$FILE $CORE_FILE -w ./$FILE.word -l ./merge/luw_mapping.txt
    $PYTHON $BASE_PROG ./$FILE $CORE_FILE -w ./$FILE.word -l ./merge/luw_mapping.txt
done
