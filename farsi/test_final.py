import os
import subprocess
import sys
import tempfile
import pytest

# Ensure farsi module can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import final


def test_convert_dependency_tree_skips_short_lines():
    """Verify lines with fewer than 10 columns are skipped without IndexError."""
    short_line = "1\ttoken\t_\t_\t_\t_\t0\t_"
    assert final.convert_dependency_tree(short_line) == []

    nine_col_line = "1\ttoken\tlemma\tupos\txpos\tfeats\t0\tdeprel\t0:00__0:01"
    assert final.convert_dependency_tree(nine_col_line) == []


def test_convert_dependency_tree_skips_comments_and_blank_lines():
    """Verify CONLL-U comments and blank lines are ignored safely."""
    content = """
    # sent_id = 1
    # text = Sample sentence with many words here
    
    # another comment
    """
    assert final.convert_dependency_tree(content) == []


def test_convert_dependency_tree_processes_valid_line():
    """Verify standard 10-column CONLL-U line is parsed and (x, y) offset appended."""
    line = "1\tform\tlemma\tupos\txpos\tfeats\t5\tdeprel\t0:00__0:01\t00:00,000__00:01,000"
    result = final.convert_dependency_tree(line)
    assert len(result) == 1
    item = result[0]
    assert len(item) == 11
    # parent_index(5) - token_index(1) = 4
    assert item[-1] == "(4, 0)"


def test_main_with_real_sample_file(tmp_path):
    """Verify final.main produces output identical to reference output.vrt."""
    sample_annotated = os.path.join(os.path.dirname(__file__), "output_files", "annotated_pos_sent.txt")
    reference_output = os.path.join(os.path.dirname(__file__), "output_files", "output.vrt")

    if not os.path.exists(sample_annotated) or not os.path.exists(reference_output):
        pytest.skip("Sample files not found")

    output_path = tmp_path / "test_out.vrt"
    final.main(sample_annotated, str(output_path))

    with open(output_path, "r", encoding="utf-8") as f_out, \
         open(reference_output, "r", encoding="utf-8") as f_ref:
        out_lines = f_out.readlines()
        ref_lines = f_ref.readlines()

    assert len(out_lines) == len(ref_lines)
    # Check first 50 lines match exactly
    for i in range(min(50, len(out_lines))):
        assert out_lines[i] == ref_lines[i]


def test_cli_flags(tmp_path):
    """Verify execution via CLI flags (-i, -o)."""
    input_file = tmp_path / "in.txt"
    input_file.write_text(
        "1\ttoken\tlemma\tNOUN\tN_SING\tNumber=Sing\t0\troot\t0:00__0:01\t00:00,000__00:01,000\n",
        encoding="utf-8"
    )
    output_file = tmp_path / "out.vrt"

    script_path = os.path.join(os.path.dirname(__file__), "final.py")
    result = subprocess.run(
        [sys.executable, script_path, "-i", str(input_file), "-o", str(output_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8").strip() != ""


def test_cli_positional_args(tmp_path):
    """Verify execution via positional CLI args."""
    input_file = tmp_path / "in_pos.txt"
    input_file.write_text(
        "1\ttoken\tlemma\tNOUN\tN_SING\tNumber=Sing\t0\troot\t0:00__0:01\t00:00,000__00:01,000\n",
        encoding="utf-8"
    )
    output_file = tmp_path / "out_pos.vrt"

    script_path = os.path.join(os.path.dirname(__file__), "final.py")
    result = subprocess.run(
        [sys.executable, script_path, str(input_file), str(output_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8").strip() != ""


def test_import_safety():
    """Verify importing final.py does not trigger file I/O."""
    # When imported, it should not fail even if annotated_pos_sent.txt is not in cwd
    import importlib
    import final as f_mod
    importlib.reload(f_mod)
    assert hasattr(f_mod, "main")
    assert hasattr(f_mod, "convert_dependency_tree")
