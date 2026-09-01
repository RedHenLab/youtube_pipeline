# Self-check for final.py.
# Run directly: python test_final.py
#
# final.py now has a __main__ guard, so it can be imported without side
# effects (previously it read/wrote files at import time).

import os
import tempfile

import final


def test_convert_dependency_tree_skips_short_lines():
    # regression: a line with fewer than 10 columns used to pass the old
    # `len(parts) < 8` guard, then crash downstream with IndexError on item[9]
    line = "1\ttoken\t_\t_\t_\t_\t0\t_"
    assert final.convert_dependency_tree(line) == []


def test_main_reads_and_writes_given_paths():
    conllu_line = "1\tform\tlemma\tupos\txpos\tfeats\t0\tdeprel\t0:00__0:01\t0:00,000__0:01,000\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "custom_input.txt")
        output_path = os.path.join(tmpdir, "custom_output.vrt")
        with open(input_path, "w", encoding="utf-8") as f:
            f.write(conllu_line)

        final.main(input_path, output_path)

        assert os.path.exists(output_path)
        with open(output_path, encoding="utf-8") as f:
            content = f.read()
        assert content.strip() != ""


if __name__ == "__main__":
    test_convert_dependency_tree_skips_short_lines()
    test_main_reads_and_writes_given_paths()
    print("all tests passed")
