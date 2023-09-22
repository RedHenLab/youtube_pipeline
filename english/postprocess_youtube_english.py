# THIS IS FOR ENGLISH WITH THE EWT MODEL

# -*- coding: utf-8 -*-
import argparse, re, sys
import json
from pathlib import Path

def xmlescape_mysql(x):
    #Function to escape certain characters so that the output is a valid xml file AND DOES NOT CONTAIN ANY CHARACTERS BEYOND THE MBP, which is required by MySQL's utf8 collation (which is not utf8mb4) as of CQPweb 3.2.31
    x = re.sub(r'&', '&amp;', x)
    x = re.sub(r'"', '&quot;', x)
    x = re.sub(r'\'', '&apos;', x)
    x = re.sub(r'>', '&gt;', x)
    x = re.sub(r'<', '&lt;', x)
    # THIS ONE SHOULD TAKE CARE OF THE MYSQL PROBLEM (taken from here https://stackoverflow.com/questions/13729638/how-can-i-filter-emoji-characters-from-my-input-so-i-can-save-in-mysql-5-5/13752628#13752628):
    try:
        # UCS-4
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    x = highpoints.sub(u'\u25FD', x)
    return x


parser = argparse.ArgumentParser()
parser.add_argument("-j", "--json_file", type=str, help="Name of\
                    JSON file written by youtube-dl")
parser.add_argument("-a", "--annotated", type=str, help="Name of\
                    annotated file")
args = parser.parse_args()

video_id = Path(args.annotated).stem
video_id = re.sub("(?<!^)\..*$", "", video_id)


#List of morphological features
# For Entglish with the EWT model:
morph_feats_list = ["Abbr", "Case", "Definite", "Degree", "Foreign", "Gender", "Mood", "Number", "NumType", "Person", "Poss", "PronType", "Reflex", "Tense", "Typo", "VerbForm", "Voice"]



#Indexing the dep_list and morph_feats_list so that it's easier to reference them

num_morph_feats = len(morph_feats_list)
morph_dict = {}
for ind,i in enumerate(morph_feats_list):
    morph_dict[i] = ind


'''
List of columns:

ATTRIBUTE word
ATTRIBUTE pos
ATTRIBUTE lemma
ATTRIBUTE wc
ATTRIBUTE lemma_wc
ATTRIBUTE lower          
ATTRIBUTE abbr
ATTRIBUTE xcase
ATTRIBUTE definite
ATTRIBUTE degree
ATTRIBUTE xforeign
ATTRIBUTE gender
ATTRIBUTE mood
ATTRIBUTE number
ATTRIBUTE numtype
ATTRIBUTE person
ATTRIBUTE poss
ATTRIBUTE prontype
ATTRIBUTE reflex
ATTRIBUTE tense
ATTRIBUTE typo
ATTRIBUTE verbform
ATTRIBUTE voice
ATTRIBUTE head
ATTRIBUTE deprel
ATTRIBUTE startsecs
ATTRIBUTE startcentisecs
ATTRIBUTE endsecs
ATTRIBUTE endcentisecs
ATTRIBUTE start_timestamp
ATTRIBUTE end_timestamp
ATTRIBUTE colour
'''

# Fields from JSON we are interested in:
#jsonfields = ["uploader", "channel_id", "full_title", "upload_date", "uploader_id", "categories", "title", "description", "duration", "tags", "id", "display_id"]
# For now only those we really need:
jsonfields = ["uploader", "channel_id", "full_title", "upload_date", "uploader_id", "title", "duration", "webpage_url"] #last one nigerian vids
jsonfields_dict = {}

# YouTube IDs are 11 characters long. So by replacing hyphens with a string that is 12 characters long, we ensure that the process is reversible and a YouTube ID never contains our replacement string:
video_id_for_cqpweb = re.sub("-", "___hyphen___", video_id)
print('<text id="y__', video_id_for_cqpweb, '" video_id="', video_id, '"',sep="", end="")
with open(args.json_file, encoding="utf-8") as infile:
    x = json.load(infile)
    for field in jsonfields:
        if field in x:
            if field=="upload_date":
                print(' upload_year="',xmlescape_mysql(str(x[field][:4])),'"', sep="",end="")
            print(' ', field, '="', xmlescape_mysql(str(x[field])), '"', sep="", end="")
    print(">")
#print('<s id="s__',video_id_for_cqpweb,'">', sep="")

with open(args.annotated, encoding="utf-8") as parsedfile:
    s_num=1
    for parsedline in parsedfile:
        line = parsedline.strip().split("\t")
        if line[0].startswith("#"):
            if line[0] =="# sent_id  1":
                print('<s id="1">')
            else:
                print('</s>\n<s id="'+str(s_num)+'">')
            s_num+=1
        if len(line) > 5:
            morph_feats_token = ['0' for k in range(num_morph_feats)]
            for feature in line[5].split('|'):
                try:
                    morph_feats_token[morph_dict[feature.split('=')[0]]] = feature.split('=')[1]
                except IndexError:
                    pass
            head=line[6]
            deprel=line[7]
            print(xmlescape_mysql(line[1]), xmlescape_mysql(line[4]), xmlescape_mysql(line[2]), xmlescape_mysql(line[3]),
              xmlescape_mysql(line[2] + "_" + line[3]), xmlescape_mysql(line[1].lower()), '\t'.join(morph_feats_token),
                  sep="\t", end="\t")
            print(head, "\t",deprel, end="\t")
            temp = line[9].split("__")
            match1 = re.match("([0-9][0-9]):([0-9][0-9]):([0-9][0-9]).([0-9][0-9][0-9])", temp[0])
            if match1:
                start_secs = int(match1.group(1))*3600+int(match1.group(2))*60+int(match1.group(3))
                istart = round(int(match1.group(4))/10)
                start_centisecs = f'{istart:02d}'
            print(start_secs, start_centisecs, sep="\t", end="\t")
            match2 = re.match("([0-9][0-9]):([0-9][0-9]):([0-9][0-9]).([0-9][0-9][0-9])", temp[1])
            if match2:
                end_secs = int(match2.group(1))*3600+int(match2.group(2))*60+int(match2.group(3))
                iend = round(int(match2.group(4))/10)
                end_centisecs = f'{iend:02d}'
            print(end_secs, end_centisecs, sep="\t", end="\t")
            print("\t".join(temp))
    print('</s>')
    print('</text>')
