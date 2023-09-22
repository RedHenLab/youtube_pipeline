#!/bin/bash


CONLL_IN="$1" #"conll_input"
TOKENIZED_IN="$2" #"puncttext"
OUTPATH="$3" #"conll_tokenized"


for c in "$CONLL_IN/*conll_input"
do
    BASENAME=${c%.conll_input}
    BASENAME=${BASENAME##$CONLL_IN}
    python3 merge_conll_somajo.py $c $TOKENIZED_IN/$BASENAME.punct > $OUTPATH/$BASENAME.conll.tok
done
