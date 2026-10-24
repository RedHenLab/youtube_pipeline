# -*- coding: utf-8 -*-
import argparse
import json
from pathlib import Path
import re
import sys
from typing import Optional


def xmlescape_mysql(x: str) -> str:
    """Escapes XML special characters and strips astral plane Unicode (emojis)

    beyond BMP (U+10000..U+10FFFF) required for MySQL utf8 (3-byte) compatibility
    in CQPweb.
    """
    x = re.sub(r'&', '&amp;', x)
    x = re.sub(r'"', '&quot;', x)
    x = re.sub(r'\'', '&apos;', x)
    x = re.sub(r'>', '&gt;', x)
    x = re.sub(r'<', '&lt;', x)
    try:
        # UCS-4
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    x = highpoints.sub(u'\u25FD', x)
    return x


def extract_video_id(annotated_path: str, json_data: dict, explicit_id: Optional[str] = None) -> str:
    """Extracts or derives a valid video ID.

    Order of precedence:
    1. Explicit video_id passed via CLI/parameter
    2. 'id' field in the metadata JSON
    3. Non-generic stem of annotated_path
    4. Fallback to 'video' if stem is generic like 'output' or empty
    """
    if explicit_id and explicit_id.strip():
        return explicit_id.strip()

    if json_data and isinstance(json_data, dict) and json_data.get("id"):
        return str(json_data["id"]).strip()

    stem = Path(annotated_path).stem
    stem = re.sub(r"(?<!^)\..*$", "", stem)

    # If annotated path is generic like 'output', 'corpus', or empty, check json metadata again
    if stem.lower() in ("output", "corpus", "") and json_data and isinstance(json_data, dict):
        if json_data.get("id"):
            return str(json_data["id"]).strip()
        if json_data.get("display_id"):
            return str(json_data["display_id"]).strip()

    return stem or "video"


def convert_to_xml(
    json_path: str,
    annotated_path: str,
    output_path: str = "corpus.vrt",
    video_id: Optional[str] = None
) -> str:
    """Converts annotated text and YouTube metadata into valid CQPweb VRT (XML) format."""
    # Load JSON metadata
    json_data = {}
    if json_path:
        with open(json_path, encoding="utf-8") as infile:
            json_data = json.load(infile)

    resolved_video_id = extract_video_id(annotated_path, json_data, video_id)
    video_id_for_cqpweb = re.sub("-", "___hyphen___", resolved_video_id)

    # Fields from JSON we are interested in:
    jsonfields = ["uploader", "channel_id", "full_title", "upload_date", "uploader_id", "title", "duration", "webpage_url"]

    # Ensure parent output directory exists if specified
    out_file_path = Path(output_path)
    if out_file_path.parent and not out_file_path.parent.exists():
        out_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(f'<text id="y__{video_id_for_cqpweb}" video_id="{resolved_video_id}"')
        for field in jsonfields:
            if field in json_data:
                if field == "upload_date":
                    outfile.write(f' upload_year="{xmlescape_mysql(str(json_data[field][:4]))}"')
                outfile.write(f' {field}="{xmlescape_mysql(str(json_data[field]))}"')
        outfile.write(">\n")

        in_sentence = False
        sent_count = 0

        with open(annotated_path, encoding="utf-8") as parsedfile:
            for parsedline in parsedfile:
                line = parsedline.strip()
                if not line:
                    continue

                if line.startswith("#"):
                    # Check if this comment specifies a sentence boundary (e.g., '# sent_id = 1' or '# sent_id 1')
                    sent_match = re.match(r"^#\s*sent_id\s*=?\s*(.+)$", line)
                    if sent_match:
                        if in_sentence:
                            outfile.write("</s>\n")
                        sent_id = sent_match.group(1).strip()
                        outfile.write(f'<s id="{sent_id}">\n')
                        in_sentence = True
                    # Other CoNLL-U comment lines (e.g., # text = ..., # newdoc) are ignored to prevent premature closure
                else:
                    # Token line
                    if not in_sentence:
                        # Auto-open first sentence for inputs lacking '# sent_id' markers (e.g., plain .vrt)
                        sent_count += 1
                        outfile.write(f'<s id="{sent_count}">\n')
                        in_sentence = True
                    outfile.write(xmlescape_mysql(line) + "\n")

            if in_sentence:
                outfile.write("</s>\n")

        outfile.write("</text>\n")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Convert annotated text and video metadata to CQPweb XML format.")
    parser.add_argument("-j", "--json_file", type=str, required=True, help="Name of JSON file written by youtube-dl / yt-dlp")
    parser.add_argument("-a", "--annotated", type=str, default="output.vrt", help="Name of annotated file (default is output.vrt)")
    parser.add_argument("-o", "--output", type=str, default="corpus.vrt", help="Path of output .vrt file (default is corpus.vrt)")
    parser.add_argument("-v", "--video_id", type=str, default=None, help="Explicit video ID (defaults to JSON metadata or input filename)")
    args = parser.parse_args()

    convert_to_xml(
        json_path=args.json_file,
        annotated_path=args.annotated,
        output_path=args.output,
        video_id=args.video_id
    )


if __name__ == "__main__":
    main()
