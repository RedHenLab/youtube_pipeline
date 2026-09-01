import argparse


def convert_dependency_tree(vrt_content):
    result = []
    for line in vrt_content.strip().split('\n'):
        parts = line.split()

        if len(parts) < 10:  # Standard CONLL-U has 10 columns (ID..MISC); skip anything shorter
            continue
        token_index = int(parts[0])
        parent_index = int(parts[6])
        x = parent_index - token_index
        y = 0
        string = str((x, y))
        parts.append(string)
        result.append(parts)
    return result


def main(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    result = convert_dependency_tree(file_contents)
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in result:
            item.pop(0)
            if item[1] == "_":
                item[1] = item[0]

            start, end = item[7].split("__")
            start_secs, start_centisecs = start.split(":")
            end_secs, end_centisecs = end.split(":")
            start_time, end_time = item[8].split("__")
            f.write(f"{item[0]}\t{item[3]}\t{item[1]}\t{item[2]}\t{item[1]}_{item[2]}\t{item[0]}\t_\t_\t{item[4]}\t_\t_\t_\t{item[9]}\t{item[6]}\t{start_secs}\t{start_centisecs}\t{end_secs}\t{end_centisecs}\t{start_time}\t{end_time}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process a UDPipe-annotated CONLL-U file into .fa.txt format.")
    parser.add_argument("-i", "--input", type=str, default="annotated_pos_sent.txt", help="Path to the UDPipe-annotated input file (default: annotated_pos_sent.txt)")
    parser.add_argument("-o", "--output", type=str, default="output.vrt", help="Path to the output file (default: output.vrt)")
    args = parser.parse_args()
    main(args.input, args.output)
