import pandas as pd
import os
from datetime import datetime, timedelta
import sys
from nltk.tokenize import WordPunctTokenizer
from hazm import word_tokenize
#from tokenizer import clitic_tokenize

def time_to_centiseconds(time_str):
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

