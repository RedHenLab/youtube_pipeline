#!/bin/bash

#indir /rawtext
#outdir /puncttext



inference_path=$1 #"/home/titan/sles/sles002h/punctuation_rh/src/inference.py"
weight_path=$2 #"/home/titan/sles/sles002h/punctuation_rh/out/weights.pt"

#file=$3
inpath=$3
outdir=$4

for i in $inpath/*en.txt
do
    f=$(basename $i .txt)
    f=${f##.*/}
    if [[ ! -f $outdir/$f.punct ]]
       then
    python3 $inference_path --pretrained-model=roberta-large --weight-path=$weight_path --cuda=False --language=en --in-file=$i --out-file=$outdir/$f.punct
#memoryhog: --cuda=False
#all files end without a punctuation mark, so we insert one at the beginning and one at the end; everything in between is handled by inference
    echo "<s> "$(cat $outdir/$f.punct) > $outdir/$f.punct
    echo " </s>" >> $outdir/$f.punct
    fi
done
