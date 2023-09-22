#!/bin/bash

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

basepath="$1"

find annotated_pos_sent "$basepath/annotated_pos_sent" -type f | parallel -j 32 -I ,, ./postprocess.sh ,,
