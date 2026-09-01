# Self-check for convert_dependency_tree() in final.py.
# Run directly: python test_final_convert_dependency_tree.py
#
# final.py has no __main__ guard and runs file I/O at import time (see
# issue #10), so the function is copied here rather than imported.

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


def test_short_line_is_skipped_not_crashed():
    # regression: a line with fewer than 10 columns used to pass the old
    # `len(parts) < 8` guard, then crash downstream with IndexError on item[9]
    line = "1\ttoken\t_\t_\t_\t_\t0\t_"
    assert convert_dependency_tree(line) == []


def test_full_conllu_line_is_processed():
    line = "1\tform\tlemma\tupos\txpos\tfeats\t0\tdeprel\tmisc1\tmisc2"
    result = convert_dependency_tree(line)
    assert len(result) == 1
    item = result[0]
    assert len(item) == 11  # 10 original columns + appended (x,y) string
    assert item[-1] == "(-1, 0)"  # parent_index(0) - token_index(1) = -1


if __name__ == "__main__":
    test_short_line_is_skipped_not_crashed()
    test_full_conllu_line_is_processed()
    print("all tests passed")
