import argparse
import os
import sys

# Optional hazm tokenizer with fallback
try:
    from hazm import word_tokenize
except ImportError:
    try:
        from nltk.tokenize import word_tokenize
    except ImportError:
        import re

        def word_tokenize(text):
            tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
            return tokens if tokens else text.split()


def parse_timestamp_ms(time_str):
    """Parse MM:SS,fff or HH:MM:SS,fff timestamp to total milliseconds."""
    clean_str = time_str.strip().replace('.', ':').replace(',', ':')
    parts = clean_str.split(':')
    if len(parts) == 3:
        minutes, seconds, ms = map(int, parts)
        return (minutes * 60 + seconds) * 1000 + ms
    elif len(parts) == 4:
        hours, minutes, seconds, ms = map(int, parts)
        return (hours * 3600 + minutes * 60 + seconds) * 1000 + ms
    else:
        raise ValueError(f"Invalid timestamp format: {time_str}")


def format_timestamp_ms(total_ms, has_hours=False):
    """Format total milliseconds to MM:SS,fff or HH:MM:SS,fff timestamp string."""
    total_seconds = total_ms // 1000
    ms = total_ms % 1000
    hours = total_seconds // 3600
    remainder = total_seconds % 3600
    minutes = remainder // 60
    seconds = remainder % 60
    if has_hours or hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"
    else:
        return f"{minutes:02d}:{seconds:02d},{ms:03d}"


def time_to_centiseconds(time_str):
    """Convert timestamp string to total_seconds:centiseconds format."""
    total_ms = parse_timestamp_ms(time_str)
    total_seconds = total_ms // 1000
    ms_remainder = total_ms % 1000
    centiseconds = round(ms_remainder / 10)
    if centiseconds >= 100:
        total_seconds += 1
        centiseconds -= 100
    return f"{total_seconds}:{centiseconds:02d}"


def convert_timeframe(start, end, text):
    """Interpolate start and end timestamps across words proportional to word length."""
    start_ms = parse_timestamp_ms(start)
    end_ms = parse_timestamp_ms(end)
    duration_ms = end_ms - start_ms

    has_hours = (len(start.replace(',', ':').split(':')) == 4 or
                 len(end.replace(',', ':').split(':')) == 4 or
                 start_ms >= 3600000 or end_ms >= 3600000)

    words = word_tokenize(text)
    if not words:
        return []

    total_characters = sum(len(word) for word in words)
    if total_characters == 0:
        total_characters = len(words)

    ms_per_char = duration_ms / total_characters

    current_ms = start_ms
    output = []

    for word in words:
        word_time = ms_per_char * len(word)
        word_end_ms = current_ms + word_time
        output.append((
            format_timestamp_ms(int(round(current_ms)), has_hours=has_hours),
            format_timestamp_ms(int(round(word_end_ms)), has_hours=has_hours),
            word
        ))
        current_ms = word_end_ms

    return output


def parse_vtt(file_path):
    """Parse WebVTT file and extract cue start, end, and caption text."""
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
            parts = line.split(' --> ')
            start = parts[0].strip().replace('.', ',')
            # Extract end timestamp before any cue settings
            end = parts[1].strip().split()[0].replace('.', ',')
        elif line and not line.startswith('WEBVTT') and not line.startswith('NOTE'):
            text.append(line)

    if start and end and text:
        captions.append((start, end, ' '.join(text)))

    return captions


def process_file(input_file, output_file):
    """Process a single .vtt file into a .conll_input file."""
    captions = parse_vtt(input_file)
    wordcount = 0

    out_dir = os.path.dirname(os.path.abspath(output_file))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for start, end, text in captions:
            output = convert_timeframe(start, end, text)
            for item in output:
                wordcount += 1
                f.write(
                    f"{wordcount}\t{item[2]}\t" + ('_\t' * 6) +
                    f"{time_to_centiseconds(item[0])}__{time_to_centiseconds(item[1])}\t"
                    f"{item[0]}__{item[1]}\n"
                )


def _get_conll_basename(filename):
    """Strip .vtt extension and optional trailing dot (e.g. video..vtt)."""
    base_name = os.path.basename(filename)
    while base_name.endswith('.vtt'):
        base_name = base_name[:-4]
    if base_name.endswith('.'):
        base_name = base_name.rstrip('.')
    return base_name


def main(vtt_target, conll_target):
    """Convert .vtt file(s) into .conll_input file(s)."""
    if os.path.isfile(vtt_target):
        if os.path.isdir(conll_target) or conll_target.endswith(('/', '\\')):
            os.makedirs(conll_target, exist_ok=True)
            base_name = _get_conll_basename(vtt_target)
            out_file = os.path.join(conll_target, f"{base_name}.conll_input")
        else:
            out_file = conll_target
        process_file(vtt_target, out_file)
    elif os.path.isdir(vtt_target):
        vtt_files = [f for f in os.listdir(vtt_target) if f.endswith('.vtt')]
        if not vtt_files:
            print(f"No .vtt files found in {vtt_target}")
            return
        os.makedirs(conll_target, exist_ok=True)
        for vf in vtt_files:
            in_file = os.path.join(vtt_target, vf)
            base_name = _get_conll_basename(vf)
            out_file = os.path.join(conll_target, f"{base_name}.conll_input")
            process_file(in_file, out_file)
    else:
        raise FileNotFoundError(f"Input path not found: {vtt_target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert WebVTT subtitle files to CONLL format (.conll_input) with word-level timestamps."
    )
    parser.add_argument(
        "vtt_path",
        help="Path to input .vtt file or directory containing .vtt files",
    )
    parser.add_argument(
        "conll_path",
        help="Path to output .conll_input file or output directory",
    )

    args = parser.parse_args()
    main(args.vtt_path, args.conll_path)
