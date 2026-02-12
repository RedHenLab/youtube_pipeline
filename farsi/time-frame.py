import pandas as pd
import os
from datetime import datetime, timedelta
import sys
from nltk.tokenize import WordPunctTokenizer
from hazm import word_tokenize
#from tokenizer import clitic_tokenize

def time_to_centiseconds(time_str):
    """
    Convert time string to seconds:centiseconds format.
    
    Supports two input formats:
    - MM:SS,FF (minutes:seconds,milliseconds)
    - HH:MM:SS,FF (hours:minutes:seconds,milliseconds)
    
    Args:
        time_str: Time string in format MM:SS,FF or HH:MM:SS,FF
        
    Returns:
        String in format "SECONDS:CENTISECONDS" (e.g., "125:03")
        
    Raises:
        ValueError: If time format is invalid
    """
    # Replace ',' with ':' and split by ':'
    time_parts = time_str.replace(',', ':').split(':')
    
    # Determine the format based on the number of parts
    if len(time_parts) == 3:  # MM:SS,FF format
        minutes, seconds, milliseconds = map(int, time_parts)
        total_seconds = minutes * 60 + seconds
    elif len(time_parts) == 4:  # HH:MM:SS,FF format
        hours, minutes, seconds, milliseconds = map(int, time_parts)
        total_seconds = hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError("Invalid time format")

    # Convert milliseconds to centiseconds
    total_centiseconds = round(milliseconds / 10)
    
    return f"{total_seconds}:{total_centiseconds:02}"


def convert_timeframe(start, end, text):
    """
    Convert a text segment with start/end times into word-level timestamps.
    
    Tokenizes the text and distributes the time duration proportionally
    across words based on character count.
    
    Args:
        start: Start time string in format '%M:%S,%f' (e.g., "01:23,456")
        end: End time string in format '%M:%S,%f'
        text: Text content to tokenize and timestamp
        
    Returns:
        List of tuples containing (start_time, end_time, word) for each token
    """
    start_time = datetime.strptime(start, '%M:%S,%f')
    end_time = datetime.strptime(end, '%M:%S,%f')
    duration = end_time - start_time

    # Adapt tokenization method:
    # Whitespace
    #words = text.split()
    #print(words)
    # WordPunctTokenizer
    # tokenizer = WordPunctTokenizer()
    words = word_tokenize(text)
    #print(words)
    # With clitics separation
    # words = clitic_tokenize(words)

    total_characters = sum(len(word) for word in words)
    word_duration = duration.total_seconds() / total_characters

    current_time = start_time
    output = []

    for word in words:
        word_time = word_duration * len(word)
        word_end_time = current_time + timedelta(seconds=word_time)
        output.append((current_time.strftime('%M:%S,%f')[:-3], word_end_time.strftime('%M:%S,%f')[:-3], word))
        current_time = word_end_time

    return output

def parse_vtt(file_path):
    """
    Parse a VTT (WebVTT) subtitle file and extract captions.
    
    Reads a WebVTT file and extracts timestamped caption blocks,
    converting them into a structured format.
    
    Args:
        file_path: Path to the VTT file to parse
        
    Returns:
        List of tuples containing (start_time, end_time, text) for each caption
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    captions = []
    start, end, text = None, None, []

    for line in lines:
        line = line.strip()
        if '-->' in line:
            if start and end and text:
                captions.append((start, end, ' '.join(text)))
                text = []
            start, end = line.split(' --> ')
            start = start.replace('.', ',')
            end = end.replace('.', ',')
        elif line and line != 'WEBVTT':
            text.append(line)

    if start and end and text:
        captions.append((start, end, ' '.join(text)))

    return captions

def main(vtt_folder, conll_input):
    """
    Main function to process VTT files and convert to CONLL format.
    
    Reads VTT subtitle files, parses captions, tokenizes text with timestamps,
    and writes output in CONLL format.
    
    Args:
        vtt_folder: Directory containing input VTT files
        conll_input: Directory for output CONLL files
    """
    input_file = os.path.join(vtt_folder, "Ckr5G4EvEdU.vtt")
    output_file = os.path.join(conll_input, "Ckr5G4EvEdU.conll_input")

    captions = parse_vtt(input_file)
    wordcount=0

    with open(output_file, 'w', encoding='utf-8') as f:
        for start, end, text in captions:
            output = convert_timeframe(start, end, text)
            #f.write(f"{item[2]}\t_\t_\t_\t_\t_\t_\t{item[0]}__{item[1]}__default \n")
            for item in output:
                wordcount+=1

                #f.write('\t'.join(item) + '\n')
                #f.write(f"1{item[2]}\t_\t_\t_\t_\t_\t_\t{item[0]}\t{item[1]}__default \n")
                f.write(f"{wordcount}\t{item[2]}\t" + ('_\t' * 6) + f"{time_to_centiseconds(item[0])}__{time_to_centiseconds(item[1])}\t{item[0]}__{item[1]}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python time_frame.py <input_output_folder>")
        sys.exit(1)
    vtt_folder = sys.argv[1]
    conll_input = sys.argv[2]
    main(vtt_folder, conll_input)

