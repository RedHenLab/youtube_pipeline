#!/bin/bash                                                                     
CORPUS_PATH=$1 #main directory for the corpus

INFERENCE_PATH=$2 #script for punctuation inference

WEIGHT_PATH=$3 # weights for punctuation inference

PATH_TO_UDPIPE_MODEL=$4 # model for linguistic annotation with UDPipe

PATH_TO_UDPIPE=$5 # UDPipe 1 installation

CORPUS_NAME=$6 #corpus name to be used as an ID in the overall corpus file. Must not contain special characters beyond underscores!

./setup_directories.sh "$CORPUS_PATH"

./convert_vtt_to_conll-u.sh "$CORPUS_PATH/vtt" "$CORPUS_PATH/conll_input"

python3 ./extract_text_connl.py "$CORPUS_PATH/conll_input" "$CORPUS_PATH/rawtext"

./infer_punctuation.sh "$INFERENCE_PATH" "$WEIGHT_PATH" "$CORPUS_PATH/rawtext" "$CORPUS_PATH/puncttext"

./tok_conll_merge.sh "$CORPUS_PATH/conll_input" "$CORPUS_PATH/puncttext" "$CORPUS_PATH/conll_tokenized"

./annotate_english_pos_sent.sh "$PATH_TO_UDPIPE_MODEL" "$PATH_TO_UDPIPE" "$CORPUS_PATH/conll_tokenized" "$CORPUS_PATH/annotated_pos_sent"

./postprocess_all.sh "$CORPUS_PATH"

./assemble_corpus.sh "$CORPUS_PATH/vertical_pos_sent" "$CORPUS_NAME"
