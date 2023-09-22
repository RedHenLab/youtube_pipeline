#!/bin/bash

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

PATH_TO_UDPIPE_MODEL=$1 #"/home/titan/sles/sles002h/ud_pipeline/models"
PATH_TO_UDPIPE=$2 #"/home/titan/sles/sles002h/ud_pipeline/udpipe/src"
PARALLEL_JOBS=2

inpath=$3
outpath=$4


find en.conll.tok $inpath -type f | xargs -P $PARALLEL_JOBS -I ,, $PATH_TO_UDPIPE/udpipe --input=conllu --tag --parse $PATH_TO_UDPIPE_MODEL/english-ewt-ud-2.5-191206.udpipe   --outfile $outpath/{}_annotated_pos_sent.txt ,,
