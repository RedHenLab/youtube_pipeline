
This repository provides a comprehensive pipeline to create a Farsi-language corpus from YouTube subtitles. The process includes downloading subtitles, generating subtitles if needed, performing linguistic annotation, and formatting the corpus for CQPweb integration.

# Prerequisites

Ensure you have the following tools and libraries installed:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading videos and subtitles.
- [OpenAI Whisper](https://github.com/openai/whisper) for generating subtitles.
- [Python](https://www.python.org/) with the following libraries:
  - `pandas`
  - `nltk`
  - `hazm`
  - `argparse`
  - `json`
- [UDPipe](https://ufal.mff.cuni.cz/udpipe) for linguistic annotation.

You also need the **Farsi Persian Seraji model** for UDPipe: `persian-seraji-ud-2.5-191206.udpipe`.

# Pipeline Overview

1. **Download Videos and Subtitles**: Use `yt-dlp` to download YouTube videos and subtitles.
2. **Handle Subtitles**:
   - If Farsi subtitles are available, run punctuation restoration.
   - If Farsi subtitles are not available, generate them using OpenAI Whisper.
3. **Process Subtitles**: Use `time_frame.py` to convert `.vtt` files to `.conllu` format.
4. **Annotate Text**: Use UDPipe to annotate the `.conllu` file and produce an annotated file.
5. **Post-process Annotation**: Convert the annotated file to `.fa.txt` using `final.py`.
6. **Convert to XML Format**: Use `convert_to_xml.py` to convert `.fa.txt` into `.vrt` format.
7. **Concatenate `.vrt` Files**: Merge multiple `.vrt` files if necessary.
8. **Upload to CQPweb**: Upload the final `.vrt` file to CQPweb.

# Detailed Steps

## Step 1: Download YouTube Videos and Subtitles

Use the following command to download videos and Farsi subtitles:

```
yt-dlp -i -o "%(id)s.%(ext)s" "URL_of_the_video" --write-info-json --write-auto-sub --sub-lang fa --verbose 
```

This command downloads the video along with its subtitles in Farsi (.vtt format).4

## Step 2: Handle Subtitles

- If Farsi subtitles exist, run the punctuation restoration model.
- If Farsi subtitles do not exist, generate subtitles using OpenAI Whisper:

```
whisper "path_to_video_file" --model large --language Persian -f 'vtt'
```
## Step 3: Process Subtitles with time_frame.py

Run the time_frame.py script to process .vtt files and convert them to .conllu format:

```
python time_frame.py path_to_vtt_folder path_to_conllu_output_folder
```

## Step 4: Annotate Text with UDPipe

Use UDPipe for tokenization, POS tagging, and dependency parsing:

```
/path/to/udpipe --input=conllu --tag --parse /path/to/persian-seraji-ud-2.5-191206.udpipe/ --outfile /path/to/output/annotated.txt /path/to/conllu/file
```

## Step 6: Convert to XML with xml.py

Run xml.py to convert .fa.txt into XML format for CQPweb:

```
python convert_to_xml.py --json_file "info.json" --annotated "output.fa.txt"
```

## Step 7: Concatenate .vrt Files

If processing multiple videos, concatenate all .vrt files:

```
cat *.vrt > combined_corpus.vrt
```

## Step 8: Upload to CQPweb

Upload the concatenated .vrt file to CQPweb to query and analyze the corpus.


# Folder Structure
```
├── time_frame.py        # Processes .vtt subtitles and generates .conllu files
├── final.py             # Post-processes annotated text into .fa.txt format
├── convert_to_xml.py               # Converts .fa.txt into .vrt format for CQPweb
├── README.md            # This file
├── info.json            # Metadata for the video from yt-dlp
├── annotated_pos_sent.txt  # Annotated file from UDPipe
└── corpus.vrt           # Final .vrt file for CQPweb

```

# Additional Notes

- Use correct paths for input/output files in each script.
- The pipeline handles cases with missing Farsi subtitles by generating them with Whisper.
