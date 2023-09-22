#!/bin/bash


INPATH=$1
CORPUS_NAME="$2"

echo "<corpus id=\"$CORPUS_NAME\">" > "$CORPUS_NAME".vrt


for FIL in $INPATH/*vrt
do
        echo $FIL
	cat $FIL >> "$CORPUS_NAME".vrt
done
echo "</corpus>" >> "$CORPUS_NAME".vrt
