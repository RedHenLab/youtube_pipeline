#!/bin/bash
# Takes as argument the full path and name of an anotated file and then creates the vertical format with additional information from the json
# At the moment, some of our json files are called .mp4.info.json, but most are just called .info.json

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

FILEPATH="$1"
BASEPATH="${FILEPATH%%/annotated_pos_sent*}"
BASENAME="${FILEPATH##*/}"
BASENAME="${BASENAME%.en.conll_annotated_pos_sent.txt}"


OUTPATH="$BASEPATH/vertical_pos_sent/"
JSONPATH="$BASEPATH/json/"
LANGUAGE=en



echo $BASENAME

if [ -e ${JSONPATH}/${BASENAME}.info.json ]; then
	python3 postprocess_youtube_english.py -a $1 -j ${JSONPATH}/${BASENAME}.info.json > ${OUTPATH}/${BASENAME}.${LANGUAGE}.vrt
else if [ -e ${JSONPATH}/${BASENAME}.mp4.info.json ]; then
	python3 postprocess_youtube_english.py -a $1 -j ${JSONPATH}/${BASENAME}.mp4.info.json > ${OUTPATH}/${BASENAME}.${LANGUAGE}.vrt
fi
fi
