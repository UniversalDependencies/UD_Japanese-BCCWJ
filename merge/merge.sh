#!/bin/sh

usage () {
    echo "Usage: $0 -c CORE_FILE"
    echo "-c: set the file of BCCWJ core file (core_SUW.txt, requirement)"
    exit 1
}

BASE_DIR=$(cd $(dirname $0); pwd)

PYTHON=python
BASE_PROG=$BASE_DIR/script/restore_word_unit_bccwj.py
SUB_PROG=$BASE_DIR/script/convert_core_suw_pkl.py
CORE_FILE=""

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

# create core_SUW.txt.pkl
echo $PYTHON $SUB_PROG $CORE_FILE
$PYTHON $SUB_PROG $CORE_FILE

for FILE in $TARGET_FILES; do
    ttt=`echo $FILE | sed -e 's/ja_bccwj-ud-\(.*\).conllu/\1/g'`
    echo $PYTHON $BASE_PROG ./$FILE $CORE_FILE ./merge/${ttt}_pos.pkl ./merge/error_outout_${ttt}.txt -w ./$FILE.word -m ./merge/misc_mapping.pkl
    $PYTHON $BASE_PROG ./$FILE $CORE_FILE ./merge/${ttt}_pos.pkl ./merge/error_outout_${ttt}.txt ./merge/${ttt}_order.txt -w ./$FILE.word -m ./merge/misc_mapping.pkl
done
