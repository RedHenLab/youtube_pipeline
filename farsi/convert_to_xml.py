# -*- coding: utf-8 -*-
import argparse
import json
import os
from pathlib import Path
import re
import sys


def xmlescape_mysql(x):
    # Function to escape certain characters so that the output is a valid xml file
    # AND DOES NOT CONTAIN ANY CHARACTERS BEYOND THE BMP, which is required by MySQL's utf8 collation
    # (which is not utf8mb4) as of CQPweb 3.2.31
    x = re.sub(r'&', '&amp;', x)
    x = re.sub(r'"', '&quot;', x)
    x = re.sub(r'\'', '&apos;', x)
    x = re.sub(r'>', '&gt;', x)
    x = re.sub(r'<', '&lt;', x)
    # THIS ONE SHOULD TAKE CARE OF THE MYSQL PROBLEM:
    try:
        # UCS-4
        highpoints = re.compile(r'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(r'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    x = highpoints.sub('\u25FD', x)
    return x


def resolve_video_id(explicit_id=None, annotated_path=None, json_data=None, json_path=None):
    """
    Resolve YouTube video ID from explicit argument, JSON metadata, or file stem.
    Avoids using generic fallback names like 'output', 'annotated', or 'corpus'.
    """
    if explicit_id:
        return explicit_id

    if json_data and isinstance(json_data, dict):
        if json_data.get("id"):
            return str(json_data["id"])
        if json_data.get("display_id"):
            return str(json_data["display_id"])

    generic_names = {"output", "annotated", "corpus", "final", "input", "info"}

    if annotated_path:
        stem = Path(annotated_path).stem
        stem = re.sub(r"(?<!^)\..*$", "", stem)
        if stem and stem.lower() not in generic_names:
            return stem

    if json_path:
        stem = Path(json_path).stem
        stem = re.sub(r"(?<!^)\..*$", "", stem).replace(".info", "")
        if stem and stem.lower() not in generic_names:
            return stem

    return "unknown"


def convert_to_xml(json_file, annotated_file, output_file="corpus.vrt", video_id=None):
    """
    Convert annotated CoNLL-U or VRT text and yt-dlp JSON metadata into CQPweb-compatible XML.
    """
    with open(json_file, "r", encoding="utf-8") as infile:
        json_meta = json.load(infile)

    resolved_id = resolve_video_id(
        explicit_id=video_id,
        annotated_path=annotated_file,
        json_data=json_meta,
        json_path=json_file
    )

    # Replace hyphens in the video ID to ensure uniqueness for CQPweb
    video_id_for_cqpweb = re.sub("-", "___hyphen___", resolved_id)

    out_dir = os.path.dirname(os.path.abspath(output_file))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    jsonfields = ["uploader", "channel_id", "full_title", "upload_date", "uploader_id", "title", "duration", "webpage_url"]

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(f'<text id="y__{video_id_for_cqpweb}" video_id="{resolved_id}"')

        for field in jsonfields:
            if field in json_meta:
                if field == "upload_date":
                    outfile.write(f' upload_year="{xmlescape_mysql(str(json_meta[field][:4]))}"')
                outfile.write(f' {field}="{xmlescape_mysql(str(json_meta[field]))}"')
        outfile.write(">\n")

        with open(annotated_file, "r", encoding="utf-8") as parsedfile:
            s_num = 1
            in_sentence = False

            for parsedline in parsedfile:
                line = parsedline.strip()
                if not line:
                    continue

                sent_id_match = re.match(r"^#\s*sent_id\s*=?\s*(\S+)", line)
                if sent_id_match:
                    sent_id = sent_id_match.group(1)
                    if in_sentence:
                        outfile.write("</s>\n")
                    outfile.write(f'<s id="{sent_id}">\n')
                    in_sentence = True
                elif line.startswith("#"):
                    # Ignore other comment lines (e.g. # text, # newdoc, # newpar)
                    continue
                else:
                    if not in_sentence:
                        outfile.write(f'<s id="{s_num}">\n')
                        in_sentence = True
                        s_num += 1
                    outfile.write(xmlescape_mysql(line) + "\n")

            if in_sentence:
                outfile.write("</s>\n")

        outfile.write("</text>\n")


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Convert annotated CoNLL-U / VRT text and yt-dlp JSON metadata into CQPweb-compatible XML format."
    )
    parser.add_argument(
        "-j", "--json_file",
        type=str,
        required=True,
        help="Path to JSON metadata file written by youtube-dl / yt-dlp",
    )
    parser.add_argument(
        "-a", "--annotated",
        type=str,
        default="output.vrt",
        help="Path to annotated file (.vrt or CoNLL-U format; default: output.vrt)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="corpus.vrt",
        help="Path to output .vrt file (default: corpus.vrt)",
    )
    parser.add_argument(
        "-v", "--video_id",
        type=str,
        default=None,
        help="Optional explicit YouTube video ID override",
    )
    return parser.parse_args(args)


def main():
    args = parse_args()
    convert_to_xml(
        json_file=args.json_file,
        annotated_file=args.annotated,
        output_file=args.output,
        video_id=args.video_id
    )


if __name__ == "__main__":
    main()
