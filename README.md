# RedHen YouTube Transcript Processing Pipeline

A pipeline for processing YouTube auto-generated captions in multiple languages to create CWB-compatible corpora in CONLL-U format with tokenization, POS tagging, lemmatization, and additional linguistic features using UDPipe.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
  - [English Processing Pipeline](#english-processing-pipeline)
  - [Persian/Farsi Processing Pipeline](#persianfarsi-processing-pipeline)
- [Input Requirements](#input-requirements)
- [Output Format](#output-format)
- [Dependencies](#dependencies)
- [Example Workflow](#example-workflow)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This pipeline processes YouTube auto-generated captions (VTT files) along with their associated JSON metadata files to produce linguistically annotated corpora in CWB-compatible CONLL-U format. The pipeline performs:
- VTT to CONLL-U conversion
- Text extraction
- Punctuation restoration
- Tokenization and merging
- POS tagging and lemmatization (via UDPipe)
- Corpus assembly

The pipeline supports both English and Persian/Farsi processing pipelines with language-specific optimizations.

## Features

- **Multi-language Support**: Dedicated pipelines for English and Persian/Farsi
- **Complete NLP Pipeline**: From raw VTT files to linguistically annotated corpora
- **Modular Design**: Each processing step is modular and can be run independently
- **CWB Compatible Output**: Produces CONLL-U format compatible with the Corpus Workbench (CWB)
- **Punctuation Restoration**: Uses specialized models to restore punctuation in auto-generated captions
- **Linguistic Annotation**: Leverages UDPipe for tokenization, POS tagging, and lemmatization

## Prerequisites

### System Requirements
- Linux or macOS environment (WSL2 on Windows also works)
- Bash shell
- Python 3.6+
- Basic command-line tools

### Required Software

#### 1. UDPipe 1
- Download and install UDPipe 1: https://ufal.mff.cuni.cz/udpipe/1
- Download language models:
  - English: https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/english-ewt-ud-2.5-191206.udpipe
  - Persian: https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3287/persian-seraji-ud-2.5-191206.udpipe

#### 2. Punctuation Restoration Models
- English: https://github.com/RedHenLab/punctuation-restoration
- Persian/Farsi: Included in the `farsi/punctuation_restoration_for_farsi/` directory

#### 3. Python Dependencies
```bash
pip install -r requirements.txt
```
(If a requirements.txt exists, otherwise basic Python 3 should suffice for the scripts)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/RedHenLab/youtube-pipeline.git
cd youtube-pipeline
```

2. Install UDPipe 1 following the instructions at https://ufal.mff.cuni.cz/udpipe/1

3. Download the required UDPipe models:
```bash
# English model
wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/english-ewt-ud-2.5-191206.udpipe -o english-ewt-ud-2.5-191206.udpipe

# Persian model  
wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3287/persian-seraji-ud-2.5-191206.udpipe -o persian-seraji-ud-2.5-191206.udpipe
```

4. Set up the punctuation restoration models:
   - English: Follow instructions in the RedHenLab punctuation-restoration repo
   - Persian: The model is already included in `/farsi/punctuation_restoration_for_farsi/`

5. Make scripts executable:
```bash
chmod +x *.sh
chmod +x english/*.sh
chmod +x farsi/*.sh
```

## Directory Structure

```
youtube_pipeline/
├── english/
│   ├── VTT_to_CONLL_u.py              # Convert VTT to initial CONLL-U
│   ├── extract_text_connl.py          # Extract plain text from CONLL-U
│   ├── infer_punctuation.sh           # Run punctuation restoration
│   ├── tok_conll_merge.sh             # Merge tokens with punctuated text
│   ├── annotate_english_pos_sent.sh   # Run UDPipe for POS tagging/lemmatization
│   ├── postprocess_all.sh             # Final post-processing
│   ├── assemble_corpus.sh             # Assemble final corpus
│   ├── setup_directories.sh           # Create necessary directories
│   ├── run_corpus_pipeline.sh         # Main execution script
│   └── setup_directories.farsi.sh     # Directory setup for Farsi
├── farsi/
│   ├── convert_to_xml.py              # Convert VTT to XML format
│   ├── final.py                       # Main Farsi processing script
│   ├── time-frame.py                  # Time frame processing
│   ├── punctuation_restoration_for_farsi/
│   │   ├── model_trainer.py           # Training script (if needed)
│   │   ├── predict.py                 # Prediction script
        │   ├── predict_punctuation.py   # Punctuation prediction
        │   └── model_test_suite.py      # Model testing
        └── README_farsi.md              # Farsi-specific instructions
├── LICENSE
└── README.md
```

## Usage

### English Processing Pipeline

The main pipeline for English processing is run via:

```bash
english/run_corpus_pipeline.sh <CORPUS_PATH> <INFERENCE_PATH> <WEIGHT_PATH> <UDPIPE_MODEL_PATH> <UDPIPE_PATH> <CORPUS_NAME>
```

Where:
- `CORPUS_PATH`: Main directory for your corpus (should contain `vtt/` subdirectory with .vtt and .json files)
- `INFERENCE_PATH`: Path to punctuation inference script (from punctuation-restoration repo)
- `WEIGHT_PATH`: Path to punctuation model weights
- `UDPIPE_MODEL_PATH`: Path to UDPipe English model (.udpipe file)
- `UDPIPE_PATH`: Path to UDPipe 1 executable
- `CORPUS_NAME`: Name for your corpus (used in output filename, no special characters except underscore)

#### Step-by-Step Execution

Alternatively, you can run each step individually for debugging:

1. **Setup directories**:
```bash
english/setup_directories.sh /path/to/your/corpus
```
Creates: `conll_input/`, `rawtext/`, `puncttext/`, `conll_tokenized/`, `annotated_pos_sent/`, `vertical_pos_sent/`

2. **Convert VTT to CONLL-U**:
```bash
english/convert_vtt_to_conll-u.sh /path/to/corpus/vtt /path/to/corpus/conll_input
```

3. **Extract plain text**:
```bash
python3 english/extract_text_connl.py /path/to/corpus/conll_input /path/to/corpus/rawtext
```

4. **Restore punctuation**:
```bash
english/infer_punctuation.sh /path/to/inference/script /path/to/weights /path/to/corpus/rawtext /path/to/corpus/puncttext
```

5. **Merge tokens with punctuated text**:
```bash
english/tok_conll_merge.sh /path/to/corpus/conll_input /path/to/corpus/puncttext /path/to/corpus/conll_tokenized
```

6. **Run UDPipe for POS tagging/lemmatization**:
```bash
english/annotate_english_pos_sent.sh /path/to/udpitch/model.udpipe /path/to/udpipe /path/to/corpus/conll_tokenized /path/to/corpus/annotated_pos_sent
```

7. **Post-process**:
```bash
english/postprocess_all.sh /path/to/corpus
```

8. **Assemble final corpus**:
```bash
english/assemble_corpus.sh /path/to/corpus/vertical_pos_sent CorpusName
```

### Persian/Farsi Processing Pipeline

See `farsi/README_farsi.md` for detailed instructions on the Persian pipeline.

The main Farsi processing script is:
```bash
python3 farsi/final.py /path/to/corpus
```

## Input Requirements

The pipeline expects input files created by [yt-dlp](https://github.com/yt-dlp/yt-dlp):

For each video, you need two files in the `vtt/` directory:
1. `{video_id}.vtt` - Auto-generated subtitles in VTT format
2. `{video_id}.info.json` - Metadata JSON file from yt-dlp

Example file structure:
```
corpus_directory/
└── vtt/
    ├── video1id.vtt
    ├── video1id.info.json
    ├── video2id.vtt
    ├── video2id.info.json
    └ ...
```

The VTT files should contain the auto-generated captions from YouTube, and the JSON files contain metadata like video title, upload date, duration, etc.

## Output Format

The pipeline produces a CWB-compatible corpus in CoNLL-U format with the following columns:

1. `ID` - Token index
2. `FORM` - Token form
3. `LEMMA` - Lemma form
4. `UPOS` - Universal part-of-speech tag
5. `XPOS` - Language-specific part-of-speech tag
6. `FEATS` - Morphological features
7. `HEAD` - Head of the current token
8. `DEPREL` - Dependency relation to the head
9. `DEPS` - Enhanced dependency graph (underscore if not available)
10. `MISC` - Miscellaneous annotations (including original VTT timing info when available)

Each sentence is separated by a blank line, and documents are separated by comment lines beginning with `#`.

## Dependencies

### Core Dependencies
- **Bash** - For shell scripts
- **Python 3.6+** - For Python scripts
- **UDPipe 1** - For tokenization, POS tagging, and lemmatization
- **wget/curl** - For downloading models (optional)

### Language-Specific Dependencies

#### English
- UDPipe English model
- English punctuation restoration model (from RedHenLab)

#### Persian/Farsi
- UDPipe Persian model
- Persian punctuation restoration model (included)

## Example Workflow

Here's a complete example of processing a small corpus:

```bash
# 1. Download videos with yt-dlp (create your VTT and JSON files first)
yt-dlp --write-auto-sub --sub-lang en --write-info-json <VIDEO_URLS>

# 2. Organize files
mkdir -p my_corpus/vtt
mv *.vtt *.info.json my_corpus/vtt/

# 3. Download required models
# UDPipe models (as shown in Installation section)
# Punctuation restoration models (follow respective repo instructions)

# 4. Make scripts executable
chmod +x english/*.sh

# 5. Run the pipeline
english/run_corpus_pipeline.sh \
  ./my_corpus \
  ./path/to/punctuation/inference.py \
  ./path/to/punctuation/weights \
  ./models/english-ewt-ud-2.5-191206.udpipe \
  ./udpipe \
  my_youtube_corpus

# 6. Find your output corpus in:
# my_corpus/vertical_pos_sent/my_youtube_corpus vertical
```

## Troubleshooting

### Common Issues

1. **"UDPipe not found" error**
   - Ensure UDPipe 1 is installed and in your PATH, or provide the full path to the executable

2. **Model loading errors**
   - Verify the paths to your .udpipe files are correct
   - Ensure you've downloaded the correct models for your language

3. **Punctuation restoration issues**
   - Make sure you're using compatible versions of the punctuation restoration models
   - Check that the input format matches what the punctuation model expects

4. **Permission errors**
   - Run `chmod +x *.sh` on all shell scripts if you encounter execution permission issues

5. **Encoding issues**
   - The pipeline assumes UTF-8 encoding. Ensure your VTT files are properly UTF-8 encoded

### Getting Help

If you encounter issues:
1. Check that all dependencies are properly installed
2. Verify file paths are correct
3. Ensure input files follow the expected naming convention
4. Consult the language-specific README files for additional guidance

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This pipeline uses and integrates several excellent open-source tools:
- [UDPipe](https://ufal.mff.cuni.cz/udpipe/) for tokenization, POS tagging, and lemmatization
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading YouTube content and metadata
- RedHenLab's punctuation restoration models
- The Universal Dependencies project for linguistic annotations

## Contact

For questions or issues, please open an issue in the GitHub repository.