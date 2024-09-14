# -*- coding: utf-8 -*-
import argparse, re, sys
import json
from pathlib import Path

def xmlescape_mysql(x):
    # Function to escape certain characters so that the output is a valid xml file AND DOES NOT CONTAIN ANY CHARACTERS BEYOND THE MBP, which is required by MySQL's utf8 collation (which is not utf8mb4) as of CQPweb 3.2.31
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
parser.add_argument("-j", "--json_file", type=str, help="Name of JSON file written by youtube-dl")
parser.add_argument("-a", "--annotated", type=str, default="output.vrt", help="Name of annotated file (default is output.vrt)")
args = parser.parse_args()

video_id = Path(args.annotated).stem
video_id = re.sub("(?<!^)\..*$", "", video_id)

# Fields from JSON we are interested in:
jsonfields = ["uploader", "channel_id", "full_title", "upload_date", "uploader_id", "title", "duration", "webpage_url"]
jsonfields_dict = {}

# Replace hyphens in the video ID to ensure uniqueness
video_id_for_cqpweb = re.sub("-", "___hyphen___", video_id)

with open("corpus.vrt", "w", encoding="utf-8") as outfile:
    outfile.write(f'<text id="y__{video_id_for_cqpweb}" video_id="{video_id}"')
    
    with open(args.json_file, encoding="utf-8") as infile:
        x = json.load(infile)
        for field in jsonfields:
            if field in x:
                if field == "upload_date":
                    outfile.write(f' upload_year="{xmlescape_mysql(str(x[field][:4]))}"')
                outfile.write(f' {field}="{xmlescape_mysql(str(x[field]))}"')
        outfile.write(">\n")
    
    with open(args.annotated, encoding="utf-8") as parsedfile:
        s_num = 1
        for parsedline in parsedfile:
            line = parsedline.strip()
            if line.startswith("#"):
                if line == "# sent_id 1":
                    outfile.write('<s id="1">\n')
                else:
                    outfile.write(f'</s>\n<s id="{s_num}">\n')
                s_num += 1
            else:
                outfile.write(xmlescape_mysql(line) + "\n")
        outfile.write('</s>\n')
    outfile.write('</text>\n')

