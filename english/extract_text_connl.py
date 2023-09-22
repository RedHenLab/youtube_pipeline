#!/usr/bin/python
import sys
import os
import re

#directory_in /conll_input
#directory_out /rawtext

directory_in=sys.argv[1]
directory_out=sys.argv[2]

#iterate over .conll_input files, split them on tabs and write column 1 to a new file, which thus only contains the raw text

for i in os.listdir(directory_in):
    infile = os.path.join(directory_in,i)
    o = os.path.basename(i).split(".")[0]
    readfile = open(infile, "r", encoding="utf-8")
    if not os.path.exists(os.path.join(directory_out,o+".en.txt")):
        writefileout = open(os.path.join(directory_out,o+".en.txt"), "w", encoding="utf-8")
        for l in readfile.readlines():
            l = l.split("\t")
            try:
                writefileout.write(l[1]+" ")
            except IndexError:
                print(o)
