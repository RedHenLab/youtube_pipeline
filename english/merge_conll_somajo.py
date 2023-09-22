#!/usr/bin/python3
import os
import re
import sys

#conll_in: original CONLL-U file (conll_input)
#token_in: file with punctuation and sentence tags (tokenized)
#outf: output CONLL-U file (conll_tokenized)

conll_in = open(sys.argv[1],"r", encoding="utf-8")
token_in = open(sys.argv[2], "r", encoding="utf-8")


conll_lines = conll_in.readlines()
token_lines = token_in.readlines()

toklist = []


for token in token_lines:
    for t in token.split(" "):
        if re.match("^(\<\/s\>)|(\<s\>)|[–,\.\?\!]+$", t):
            toklist.append("INSERTION"+t.strip("\n"))
        elif t=="\n":
            continue
        else:
            toklist.append(t.strip("\n"))

for t in toklist:
    if len(t)==0:
        toklist.remove(t)

t_index= 0
sent_index = 1
line_index = 1


for c in conll_lines:
    c_line = c.split("\t")
    c_tok = c_line[1]
    
    while toklist[t_index].startswith("INSERTION"):
        if toklist[t_index].endswith("</s>"):
            print()
            t_index+=1
            line_index=1
        elif toklist[t_index].endswith("<s>"):
            print("# sent_id ", sent_index)
            sent_index+=1
            t_index +=1
        else:
            print(line_index,"\t",toklist[t_index][len("INSERTION"):],"\t","_\t"*7,c_line[-1].strip("\n"),sep="")
            t_index+=1
            line_index+=1
        
    if toklist[t_index] == c_tok:
        print(line_index,"\t",toklist[t_index],"\t","_\t"*7,c_line[-1].strip("\n"),sep="")
        t_index+=1
        line_index+=1
        continue
    else:
        print(line_index, "\t", toklist[t_index], "\t", "_\t"*7, c_line[-1].strip("\n"), sep="")
        line_index+=1
        continue
