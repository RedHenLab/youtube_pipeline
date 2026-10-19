import argparse
import sys


def convert_dependency_tree(vrt_content):
    result = []
    for line in vrt_content.strip().split('\n'):
        line = line.strip()
        # Skip empty lines and CONLL-U comment / metadata lines
        if not line or line.startswith('#'):
            continue

        parts = line.split('\t')
        if len(parts) == 1:
            parts = line.split()

        # CONLL-U format requires 10 columns (ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC)
        if len(parts) < 10:
            continue

        try:
            token_index = int(parts[0])
            parent_index = int(parts[6])
        except ValueError:
            continue

        x = parent_index - token_index
        y = 0
        string = str((x, y))
        parts.append(string)
        result.append(parts)
    return result


def main(input_file="annotated_pos_sent.txt", output_file="output.vrt"):
    with open(input_file, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    result = convert_dependency_tree(file_contents)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in result:
            item.pop(0)

            if item[1] == "_":
                item[1] = item[0]

            try:
                start, end = item[7].split("__")
                start_secs, start_centisecs = start.split(":")
                end_secs, end_centisecs = end.split(":")
                start_time, end_time = item[8].split("__")
            except (ValueError, IndexError):
                continue

            f.write(
                f"{item[0]}\t{item[3]}\t{item[1]}\t{item[2]}\t{item[1]}_{item[2]}\t"
                f"{item[0]}\t_\t_\t{item[4]}\t_\t_\t_\t{item[9]}\t{item[6]}\t"
                f"{start_secs}\t{start_centisecs}\t{end_secs}\t{end_centisecs}\t"
                f"{start_time}\t{end_time}\n"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post-process a UDPipe-annotated CONLL-U file into .vrt format."
    )
    parser.add_argument(
        "input_pos",
        nargs="?",
        default=None,
        help="Path to the UDPipe-annotated input file (positional)",
    )
    parser.add_argument(
        "output_pos",
        nargs="?",
        default=None,
        help="Path to the output .vrt file (positional)",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_flag",
        default=None,
        help="Path to the UDPipe-annotated input file (default: annotated_pos_sent.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_flag",
        default=None,
        help="Path to the output .vrt file (default: output.vrt)",
    )

    args = parser.parse_args()

    input_path = args.input_flag or args.input_pos or "annotated_pos_sent.txt"
    output_path = args.output_flag or args.output_pos or "output.vrt"

    main(input_path, output_path)
