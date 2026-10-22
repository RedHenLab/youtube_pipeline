import importlib
import os
import subprocess
import sys
import tempfile
import pytest

# Dynamic import of time-frame module due to hyphen in filename
time_frame = importlib.import_module("time-frame")


class TestTimestampParsing:
    def test_parse_timestamp_ms_3_parts_comma(self):
        assert time_frame.parse_timestamp_ms("01:23,456") == (1 * 60 + 23) * 1000 + 456

    def test_parse_timestamp_ms_3_parts_dot(self):
        assert time_frame.parse_timestamp_ms("00:02.100") == 2100

    def test_parse_timestamp_ms_4_parts_comma(self):
        assert time_frame.parse_timestamp_ms("01:02:03,456") == (1 * 3600 + 2 * 60 + 3) * 1000 + 456

    def test_parse_timestamp_ms_4_parts_dot(self):
        assert time_frame.parse_timestamp_ms("00:00:02.100") == 2100

    def test_parse_timestamp_ms_large_hours(self):
        assert time_frame.parse_timestamp_ms("25:00:00.000") == 25 * 3600 * 1000

    def test_parse_timestamp_ms_invalid(self):
        with pytest.raises(ValueError):
            time_frame.parse_timestamp_ms("invalid")
        with pytest.raises(ValueError):
            time_frame.parse_timestamp_ms("01:23")


class TestTimestampFormatting:
    def test_format_under_hour_no_flag(self):
        assert time_frame.format_timestamp_ms(2100, has_hours=False) == "00:02,100"

    def test_format_under_hour_with_flag(self):
        assert time_frame.format_timestamp_ms(2100, has_hours=True) == "00:00:02,100"

    def test_format_over_one_hour(self):
        total_ms = (1 * 3600 + 10 * 60 + 5) * 1000 + 250
        assert time_frame.format_timestamp_ms(total_ms, has_hours=False) == "01:10:05,250"

    def test_format_over_24_hours(self):
        total_ms = (25 * 3600 + 1 * 60 + 1) * 1000 + 50
        assert time_frame.format_timestamp_ms(total_ms) == "25:01:01,050"


class TestCentisecondsConversion:
    def test_time_to_centiseconds_3_parts(self):
        assert time_frame.time_to_centiseconds("00:02,100") == "2:10"

    def test_time_to_centiseconds_4_parts(self):
        assert time_frame.time_to_centiseconds("00:00:02.100") == "2:10"

    def test_time_to_centiseconds_over_one_minute(self):
        assert time_frame.time_to_centiseconds("01:05,500") == "65:50"

    def test_time_to_centiseconds_rounding_up(self):
        assert time_frame.time_to_centiseconds("00:02,355") == "2:36"

    def test_time_to_centiseconds_centisecond_rollover(self):
        # 995 ms rounds to 100 centiseconds -> 1 second + 00 centiseconds
        assert time_frame.time_to_centiseconds("00:00,996") == "1:00"


class TestConvertTimeframe:
    def test_convert_timeframe_basic(self):
        output = time_frame.convert_timeframe("00:00,000", "00:02,000", "hello world")
        assert len(output) == 2
        assert output[0][2] == "hello"
        assert output[1][2] == "world"
        assert output[0][0] == "00:00,000"
        assert output[1][1] == "00:02,000"

    def test_convert_timeframe_preserves_hours_format(self):
        output = time_frame.convert_timeframe("00:00:00,000", "00:00:02,000", "test word")
        assert len(output) == 2
        assert len(output[0][0].split(":")) == 3  # HH:MM:SS,fff format has 2 colons
        assert output[0][0].startswith("00:00:")

    def test_convert_timeframe_empty_text(self):
        assert time_frame.convert_timeframe("00:00,000", "00:02,000", "") == []

    def test_convert_timeframe_continuity(self):
        output = time_frame.convert_timeframe("00:01,000", "00:05,000", "first second third")
        assert len(output) == 3
        # End of token 0 should match start of token 1
        assert output[0][1] == output[1][0]
        # End of token 1 should match start of token 2
        assert output[1][1] == output[2][0]
        # Start and end boundaries match
        assert output[0][0] == "00:01,000"
        assert output[2][1] == "00:05,000"


class TestParseVtt:
    def test_parse_vtt_basic(self, tmp_path):
        vtt_content = (
            "WEBVTT\n\n"
            "00:00.000 --> 00:02.100\n"
            "Hello world\n\n"
            "00:02.100 --> 00:04.400\n"
            "Second caption\n"
        )
        vtt_file = tmp_path / "test.vtt"
        vtt_file.write_text(vtt_content, encoding="utf-8")

        captions = time_frame.parse_vtt(str(vtt_file))
        assert len(captions) == 2
        assert captions[0] == ("00:00,000", "00:02,100", "Hello world")
        assert captions[1] == ("00:02,100", "00:04,400", "Second caption")

    def test_parse_vtt_with_cue_settings_and_notes(self, tmp_path):
        vtt_content = (
            "WEBVTT - test file\n\n"
            "NOTE this is a comment\n\n"
            "00:00:01.000 --> 00:00:03.500 line:0 position:20% align:start\n"
            "Caption with settings\n"
        )
        vtt_file = tmp_path / "test_settings.vtt"
        vtt_file.write_text(vtt_content, encoding="utf-8")

        captions = time_frame.parse_vtt(str(vtt_file))
        assert len(captions) == 1
        assert captions[0][0] == "00:00:01,000"
        assert captions[0][1] == "00:00:03,500"
        assert captions[0][2] == "Caption with settings"


class TestProcessFile:
    def test_process_file_format(self, tmp_path):
        vtt_content = (
            "WEBVTT\n\n"
            "00:00.000 --> 00:02.000\n"
            "First second\n"
        )
        vtt_file = tmp_path / "sample.vtt"
        conll_file = tmp_path / "sample.conll_input"
        vtt_file.write_text(vtt_content, encoding="utf-8")

        time_frame.process_file(str(vtt_file), str(conll_file))
        assert conll_file.exists()

        lines = conll_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

        col_parts_0 = lines[0].split("\t")
        assert len(col_parts_0) == 10
        assert col_parts_0[0] == "1"
        assert col_parts_0[1] == "First"
        assert col_parts_0[2:8] == ["_"] * 6
        assert "__" in col_parts_0[8]
        assert "__" in col_parts_0[9]

        col_parts_1 = lines[1].split("\t")
        assert len(col_parts_1) == 10
        assert col_parts_1[0] == "2"
        assert col_parts_1[1] == "second"


    def test_process_file_with_sample_vtt(self, tmp_path):
        sample_vtt = os.path.join(os.path.dirname(__file__), "output_files", "Ckr5G4EvEdU..vtt")
        if not os.path.isfile(sample_vtt):
            pytest.skip("Sample VTT file not found")

        out_conll = tmp_path / "sample_out.conll_input"
        time_frame.process_file(sample_vtt, str(out_conll))
        assert out_conll.exists()

        lines = out_conll.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) > 2000

        # Verify first line structure
        cols = lines[0].split("\t")
        assert cols[0] == "1"
        assert cols[1] == "لحظه"
        assert cols[8] == "0:00__0:56"
        assert cols[9] == "00:00,000__00:00,560"


class TestMainCLI:
    def test_main_file_to_file(self, tmp_path):
        vtt_file = tmp_path / "input.vtt"
        vtt_file.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nHello\n", encoding="utf-8")
        out_file = tmp_path / "custom_output.conll_input"

        time_frame.main(str(vtt_file), str(out_file))
        assert out_file.exists()
        assert "Hello" in out_file.read_text(encoding="utf-8")

    def test_main_file_to_dir(self, tmp_path):
        vtt_file = tmp_path / "video1..vtt"
        vtt_file.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nTest\n", encoding="utf-8")
        out_dir = tmp_path / "out_dir"
        out_dir.mkdir()

        time_frame.main(str(vtt_file), str(out_dir))
        expected_conll = out_dir / "video1.conll_input"
        assert expected_conll.exists()

    def test_main_dir_to_dir(self, tmp_path):
        in_dir = tmp_path / "vtt_in"
        in_dir.mkdir()
        out_dir = tmp_path / "conll_out"

        (in_dir / "a.vtt").write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nOne\n", encoding="utf-8")
        (in_dir / "b.vtt").write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nTwo\n", encoding="utf-8")

        time_frame.main(str(in_dir), str(out_dir))
        assert (out_dir / "a.conll_input").exists()
        assert (out_dir / "b.conll_input").exists()

    def test_main_empty_dir(self, tmp_path, capsys):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        out_dir = tmp_path / "out"

        time_frame.main(str(empty_dir), str(out_dir))
        captured = capsys.readouterr()
        assert "No .vtt files found" in captured.out

    def test_main_nonexistent_input(self):
        with pytest.raises(FileNotFoundError):
            time_frame.main("nonexistent_path_xyz", "out")

    def test_cli_execution_subprocess(self, tmp_path):
        vtt_file = tmp_path / "cli_test.vtt"
        conll_file = tmp_path / "cli_test.conll_input"
        vtt_file.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nCLI Works\n", encoding="utf-8")

        script_path = os.path.join(os.path.dirname(__file__), "time-frame.py")
        result = subprocess.run(
            [sys.executable, script_path, str(vtt_file), str(conll_file)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert conll_file.exists()
        conll_text = conll_file.read_text(encoding="utf-8")
        assert "CLI" in conll_text
        assert "Works" in conll_text
