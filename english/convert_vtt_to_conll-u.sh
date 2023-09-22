#!/bin/bash

#INPATH /vtt
#OUTPATH /conll_input

INPATH=$1
OUTPATH=$2

for i in $INPATH/*en.vtt
do
    BASENAME=${i##*/}
    BASENAME=${BASENAME%.vtt}
    if [[ ! -f $OUTPATH/$BASENAME.conll_input ]]
        then
	python3 vtt_auto_to_conll-u.py $i >${OUTPATH}/${BASENAME}.conll_input
    fi
done
