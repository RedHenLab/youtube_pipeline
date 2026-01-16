# YouTube Caption Processing Pipeline

## What Does This Project Do? 🎯

Ever watched a YouTube video with auto-generated captions? This project takes those captions and transforms them into professional, structured text data that researchers can use.

**In simple terms:** YouTube caption files → Clean, organized, analyzable text data with grammar information

This is useful for:
- **Linguists** studying how people speak
- **Researchers** building language datasets
- **Students** learning about text processing pipelines

The pipeline takes YouTube's auto-generated captions and adds:
- Proper **sentence boundaries** and punctuation
- **Grammar tags** (what part of speech each word is)
- **Timestamps** (when each word was spoken)
- **Metadata** (video info, language, etc.)

The scripts are written in Bash and Python 3.

## 🚀 Quick Start (5 Minutes!)

**Just want to see it work?**

1. Clone this repo: `git clone https://github.com/RedHenLab/youtube_pipeline.git`
2. Look at the `english/` folder to see example scripts
3. Check the Workflow section below to understand the steps
4. Read **Contributing** to get started with a small doc or bugfix

**Not ready to run it yet?** No problem — understanding this README is a great first contribution.

---

## Prerequisites

Before running this pipeline, you'll need to install three main tools. Here's what each one does:

1. **UDPipe** - Analyzes text to identify parts of speech (verb, noun, adjective, etc.)
   - Installation: https://ufal.mff.cuni.cz/udpipe/1
   - You also need the language model for your language (e.g., English model available from Lindat)

2. **Punctuation Restoration Tool** - Adds missing punctuation (periods, question marks) that YouTube captions often lack
   - Installation: https://github.com/RedHenLab/punctuation-restoration
   - You'll also need the `weights.pt` file (about 1.4 GB)

3. **SoMaJo** - Tokenizer that breaks text into correct words/tokens
   - Installation: https://github.com/tsproisl/SoMaJo/tree/master/somajo

System requirements: Linux or macOS recommended; 8+ GB RAM and ~10 GB free disk space (weights and intermediate files).

## Downloading captions

Use `yt-dlp` to download auto-generated subtitles and metadata. We recommend using the video ID as filename to avoid encoding issues.

Example:
```
yt-dlp -i -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=jNQXAC9IVRw" --skip-download --write-info-json --write-auto-sub --sub-lang en --verbose
```

Update `yt-dlp` before big download sessions:
```
pip install --upgrade yt-dlp
```

## Workflow

### Overview
The pipeline transforms YouTube captions through a series of steps. Each step adds or refines information (punctuation, tokens, grammar tags, timestamps, metadata) until the result is a corpus file ready for analysis.

### Getting Started
Before you begin, organize your files:
- Put `.vtt` caption files in a `vtt/` folder
- Put `.json` metadata files in a `json/` folder
- (Optional) Put video files in a `webm/` folder

Create processing directories:
```
./english/setup_directories.sh /path/to/your/corpus
```

### Steps (simple)

0.5 Create processing directories (`conll_input`, `rawtext`, `puncttext`, `conll_tokenized`, `annotated_pos_sent`, `vertical_pos_sent`)

1. Convert `.vtt` to CONLL (`convert_vtt_auto_to_conll-u.sh`)
- Calls `vtt_auto_to_conll-u.py`, tokenizes with SoMaJo, keeps timestamps.

2. Extract raw text (`extract_text_connl.py`)
- Pulls token column into plain text files for punctuation restoration.

3. Restore punctuation (`infer_punctuation.sh`)
- Uses the punctuation restoration tool to add punctuation and `<s>`/`</s>` sentence tags.

4. Merge tokens with timestamps (`tok_conll_merge.sh`)
- Merges punctuated text back into CONLL files while preserving timestamps.

5. Annotate with UDPipe (`annotate_english_pos_sent.sh`)
- Adds POS tags, lemmas, and syntactic information.

6. Postprocess to CWB format (`postprocess_all.sh`)
- Adds metadata and converts to `.vrt` files ready for corpus tools.

### Run everything automatically
If you want to run all steps in one command, here's a concrete example (replace paths with yours):
```
./english/run_corpus_pipeline.sh /home/alice/corpus /home/alice/punct_tool/src/inference.py /home/alice/punct_tool/weights.pt /home/alice/udpipe/models /home/alice/udpipe/src my_corpus
```
Explanation: `CORPUS_PATH` is your base folder (with `vtt/` and `json/`), `INFERENCE_PATH` points to the punctuation tool's `inference.py`, `WEIGHT_PATH` is the `weights.pt` file, `PATH_TO_UDPIPE_MODEL` and `PATH_TO_UDPIPE` point to your UDPipe installation, and `CORPUS_NAME` is a short id for the output corpus.

Tip: run individual steps first (e.g., convert one `.vtt`) to confirm paths and tools before the full run.

## How to cite
```
@inproceedings{dykes-et-al-2023-youtube,
  title = "A Pipeline for the Creation of Multimodal Corpora from YouTube Videos",
  author = "Dykes, Nathan and Uhrig, Peter and Wilson, Anna",
  booktitle = "Proceedings of KONVENS 2023",
  year = "to appear"
}
```

## Contributing

Want to contribute? Start small — docs are the best first contribution.

- Improve documentation (this README or script comments)
- Report issues with steps you tried
- Add a small example or one new language support
- Fix a typo or improve error messages in scripts

First-time contributor checklist:

1. Fork the repo and create a branch
2. Make a small, focused change (e.g., README clarification)
3. Run any relevant scripts locally (if you can)
4. Open a Pull Request explaining what you changed and why

## Glossary

- CONLL Format: a standard tabular text format for linguistic annotations
- UDPipe: tool for POS tagging, lemmatisation and parsing
- Tokenization: splitting text into words/tokens
- POS Tagging: labeling each word with its part-of-speech
- Lemmatization: finding a word's base/dictionary form
- CWB (Corpus Workbench): tools for corpus search and analysis
- VTT: Video Text Track (YouTube captions)

## Acknowledgements
This work was supported by funding to Peter Uhrig and Anna Wilson and by computing resources from NHR@FAU. See original repository for full acknowledgements.

