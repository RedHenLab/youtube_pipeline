#!/bin/bash                                                                     
INPATH=$1

if [ $# -eq 0 ]
then
    echo "Please provide the path to your corpus directory when calling this script."
else
    mkdir "$INPATH/conll_input"
    mkdir "$INPATH/rawtext"
    mkdir "$INPATH/puncttext"
    mkdir "$INPATH/conll_tokenized"
    mkdir "$INPATH/annotated_pos_sent"
    mkdir "$INPATH/vertical_pos_sent"
fi
