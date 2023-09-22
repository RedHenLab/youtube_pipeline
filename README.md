Pipeline to process YouTube auto-generated captions in multiple languages
For a given collection of auto-captions and json metadata, the pipeline produces a CWB-compatible corpus in CONLL format with tokenisation, POS tagging, lemmatisation and further token-level features as created by UDPipe.

Scripts are written in bash and Python 3.

## Input files ##
The pipeline takes as input files created by the Python library [yt-dlp](https://pypi.org/project/yt-dlp/)
You will need the auto-generated subtitles (.vtt files) along with accompanying json files (for metadata)

## Prerequisites ##
- You will need an installation of UDPipe 1, along with the relevant model for the language in question ([https://ufal.mff.cuni.cz/udpipe/1](https://ufal.mff.cuni.cz/udpipe/1); English model: [https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/english-ewt-ud-2.5-191206.udpipe](https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/english-ewt-ud-2.5-191206.udpipe)).
- You will need an installation of our fork of Alam et al.2020's punctuation restoration tool ([https://github.com/RedHenLab/punctuation-restoration)](https://github.com/RedHenLab/punctuation-restoration)) and [our weights file](http://go.redhenlab.org/pgu/punctuation_restoration/) (1.4 GB)
- You will need an installation of SoMaJo for tokenisation (https://github.com/tsproisl/SoMaJo/tree/master/somajo)

## Download ##
To avoid problems with strange characters in filenames, we recommend using the YouTube video ID as filename. The following command will download the auto-generated subtitles and the info json file, but will not download the video:
```
yt-dlp -i -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=jNQXAC9IVRw" --skip-download --write-info-json --write-auto-sub --sub-lang en --verbose
```
Note that yt-dlp regularly needs to be updated to continue working. We recommend running
```
pip install --upgrade yt-dlp
```
before each download session.

## Workflow ##

0. The scripts assume that you have the following directories in the directory where you want to build your corpus:
- `vtt` contains your .vtt files
- `json` contains the associated .json files
- `webm` contains the video files

In order to go through all corpus processing steps automatically, you can run

```run_corpus_pipeline.sh CORPUS_PATH INFERENCE_PATH WEIGHT_PATH PATH_TO_UDPIPE_MODEL PATH_TO_UDPIPE CORPUS_NAME```

with the following arguments:
CORPUS_PATH: directory containing the `vtt`, `json` and `webm` directories. The results for other intermediate steps will be stored here.
INFERENCE_PATH points to the inference script for punctuation restoration. In our repository, this is stored in src/inference.py in the punctuation tool's directory.
WEIGHT_PATH points to the `weights.pt` file used for punctuation restoration.
PATH_TO_UDPIPE_MODEL points to the `models` directory of your UDPipe installation
PATH_TO_UDPIPE points to the `src` directory of your UDPipe installation
CORPUS_NAME specifies the CWB ID for your corpus

0.5 run `setup_directories.sh`, passing your desired base directory as an argument to create the following empty directories:
    - `connl_input` for step 1.
    - `rawtext` for step 2.
    - `puncttext` for step 3.
    - `conll_tokenized` for step 4.
    - `annotated_pos_sent` for step 5.
    - `vertical_pos_sent` for step 6.
    
1. `convert_vtt_auto_to_conll-u.sh` Convert your .vtt files to CONLL
This script assumes the existence of a directory called `conll_input` and takes as input the .vtt file that you would like to convert to CONLL format.

It then calls `vtt_auto_to_conll-u.py` on the specified .vtt file and produces a corresponding `.conll_input`file, which consists of a tab-separated line number, the "token", several "empty" columns with underscores and the start and end time for each word. Tokenisation is done with the help of SoMaJo -- this also means that we do not retain the multi-word units in the vtt files, such as "a little". Instead in such cases, each individual token is set to the same start and end time.

2. `extract_text_connl.py`
This script takes as input the path of the non-annotated ConLL-files from their directory. It writes the content of the "token" column to a raw-text file, which can then be processed by NLP tools.

3. `infer_punctuation.sh`
Calls Alam et al.'s punctuation tool to insert punctuation marks. For this pipeline, we modified the inference script to insert not only the punctuation marks themselves, but also sentence-opening and closing XML tags (<s>, </s>) in after sentence-ending characters [\.\?!]. This script completes the sentence boundary marking for each file by inserting one opening tag in the beginning and one closing tag at the end.
The script's input consists of the inference path, the weights path, the directory with raw texts and the output directory puncttext.

4. `tok_conll_merge.sh`
The tokenized files now need to be merged with the "old" ConLL-files before tagging, because these still contain the timestamps for all original tokens. The shell script takes as input a the conll_input directory and the puncttext/ directory, and calls `merge_conll_somajo.py` to handle the merging process. Output is stored in `conll_tokenized`.

5. `annotate_english_pos_sent.sh`
takes as input path to the UDPipe model, the path to the src/ folder of UDPipe, the conll_tokenized folder and annotates them with UDPipe (POS tagging and parsing), writing them to annotated_pos_sent/.

6. `postprocess_all.sh`
Takes as an argument the directory containing the sub-directories for individual processing steps, and calls postprocess.sh, which in turn calls `postprocess_youtube_english.py`. This script reads information from the JSON file as text-level metadata and changes the formatting of sentence and token level annotation to match the CWB input format. It creates a .vrt file for each corpus text.

## How to cite ##
```
@inproceedings{dykes-et-al-2023-youtube,
    title = "A Pipeline for the Creation of Multimodal Corpora from YouTube Videos",
    author = "Dykes, Nathan  and
      Uhrig, Peter  and
      Wilson, Anna",
    booktitle = "Proceedings of KONVENS 2023",
    year = "to appear"
}
```
## Acknowledgements ##
