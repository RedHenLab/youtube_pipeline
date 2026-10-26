import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import pytest

from convert_to_xml import xmlescape_mysql, resolve_video_id, convert_to_xml, parse_args


class TestXmlEscape:
    def test_escape_special_characters(self):
        text = 'Tom & Jerry: "Cat" > <dog> \'tail\''
        escaped = xmlescape_mysql(text)
        assert '&amp;' in escaped
        assert '&quot;' in escaped
        assert '&gt;' in escaped
        assert '&lt;' in escaped
        assert '&apos;' in escaped

    def test_filter_emoji_beyond_bmp(self):
        text = 'Hello \U0001F600 World'  # grinning face emoji
        escaped = xmlescape_mysql(text)
        assert '\U0001F600' not in escaped
        assert '\u25FD' in escaped


class TestResolveVideoId:
    def test_explicit_id_takes_precedence(self):
        assert resolve_video_id(explicit_id="custom_id", json_data={"id": "json_id"}) == "custom_id"

    def test_id_from_json(self):
        assert resolve_video_id(json_data={"id": "Ckr5G4EvEdU"}) == "Ckr5G4EvEdU"

    def test_display_id_from_json(self):
        assert resolve_video_id(json_data={"display_id": "disp123"}) == "disp123"

    def test_avoids_generic_annotated_name(self):
        vid = resolve_video_id(annotated_path="output.vrt", json_data={"id": "real_id"})
        assert vid == "real_id"

    def test_from_annotated_filename(self):
        vid = resolve_video_id(annotated_path="video123.vrt", json_data={})
        assert vid == "video123"

    def test_fallback_unknown(self):
        vid = resolve_video_id()
        assert vid == "unknown"


class TestConvertCoNLLU:
    def test_conllu_with_sent_ids_and_comments(self, tmp_path):
        json_file = tmp_path / "meta.info.json"
        json_file.write_text(json.dumps({
            "id": "test-vid-1",
            "title": "Test Title",
            "upload_date": "20231015",
            "uploader": "Tester"
        }), encoding="utf-8")

        annotated_file = tmp_path / "annotated.conllu"
        annotated_file.write_text(
            "# newdoc id = doc1\n"
            "# newpar\n"
            "# sent_id = 1\n"
            "# text = First sentence\n"
            "1\tFirst\tfirst\tADJ\t_\t_\t2\tamod\t_\t_\n"
            "2\tsentence\tsentence\tNOUN\t_\t_\t0\troot\t_\t_\n"
            "\n"
            "# sent_id = 2\n"
            "# text = Second sentence\n"
            "1\tSecond\tsecond\tADJ\t_\t_\t2\tamod\t_\t_\n"
            "2\tsentence\tsentence\tNOUN\t_\t_\t0\troot\t_\t_\n",
            encoding="utf-8"
        )

        out_file = tmp_path / "out.vrt"
        convert_to_xml(str(json_file), str(annotated_file), str(out_file))

        assert out_file.exists()
        xml_content = out_file.read_text(encoding="utf-8")

        # Parse with standard XML parser to guarantee well-formedness
        root = ET.fromstring(xml_content)
        assert root.tag == "text"
        assert root.attrib["video_id"] == "test-vid-1"
        assert root.attrib["id"] == "y__test___hyphen___vid___hyphen___1"
        assert root.attrib["upload_year"] == "2023"

        sentences = root.findall("s")
        assert len(sentences) == 2
        assert sentences[0].attrib["id"] == "1"
        assert sentences[1].attrib["id"] == "2"


class TestConvertVRTWithoutSentences:
    def test_vrt_plain_tokens_wrapped_properly(self, tmp_path):
        # Like output.vrt from final.py which has no # sent_id lines
        json_file = tmp_path / "meta.json"
        json_file.write_text(json.dumps({
            "id": "vid99",
            "title": "Plain VRT"
        }), encoding="utf-8")

        annotated_file = tmp_path / "output.vrt"
        annotated_file.write_text(
            "Word1\tNOUN\tword1\tNOUN\tword1_NOUN\tWord1\t_\t_\tNumber=Sing\t_\t_\t_\t(0, 0)\troot\t0\t00\t0\t50\t00:00,000\t00:00,500\n"
            "Word2\tVERB\tword2\tVERB\tword2_VERB\tWord2\t_\t_\tNumber=Sing\t_\t_\t_\t(0, 0)\troot\t0\t50\t1\t00\t00:00,500\t00:01,000\n",
            encoding="utf-8"
        )

        out_file = tmp_path / "out_plain.vrt"
        convert_to_xml(str(json_file), str(annotated_file), str(out_file))

        assert out_file.exists()
        xml_content = out_file.read_text(encoding="utf-8")

        # This must not fail with mismatched </s> tag!
        root = ET.fromstring(xml_content)
        assert root.tag == "text"
        sentences = root.findall("s")
        assert len(sentences) == 1
        assert sentences[0].attrib["id"] == "1"
        assert "Word1" in sentences[0].text or "Word1" in xml_content


class TestCustomOutputAndDirectoryCreation:
    def test_creates_nested_output_directory(self, tmp_path):
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps({"id": "nested_vid"}), encoding="utf-8")

        annotated_file = tmp_path / "test.vrt"
        annotated_file.write_text("Token\tNOUN\n", encoding="utf-8")

        nested_out = tmp_path / "deep" / "nested" / "dir" / "result.vrt"
        convert_to_xml(str(json_file), str(annotated_file), str(nested_out), video_id="nested_vid")

        assert nested_out.exists()
        root = ET.fromstring(nested_out.read_text(encoding="utf-8"))
        assert root.attrib["video_id"] == "nested_vid"


class TestSampleFilesIntegration:
    def test_sample_files_produce_valid_xml(self, tmp_path):
        sample_json = os.path.join(os.path.dirname(__file__), "output_files", "Ckr5G4EvEdU.info.json")
        sample_vrt = os.path.join(os.path.dirname(__file__), "output_files", "output.vrt")

        if not os.path.isfile(sample_json) or not os.path.isfile(sample_vrt):
            pytest.skip("Sample files not found")

        out_file = tmp_path / "sample_corpus.vrt"
        convert_to_xml(sample_json, sample_vrt, str(out_file))

        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")

        # Must parse cleanly with ET
        root = ET.fromstring(content)
        assert root.attrib["video_id"] == "Ckr5G4EvEdU"
        assert root.attrib["id"] == "y__Ckr5G4EvEdU"
        assert root.attrib["uploader"] == "MoboNews"
        assert root.attrib["upload_year"] == "2023"

        # Verify sentences exist and are properly closed
        sentences = root.findall("s")
        assert len(sentences) >= 1


class TestCommandLineInterface:
    def test_cli_execution_subprocess(self, tmp_path):
        json_file = tmp_path / "cli.json"
        json_file.write_text(json.dumps({"id": "cli_vid", "title": "CLI Test"}), encoding="utf-8")

        annotated_file = tmp_path / "cli.vrt"
        annotated_file.write_text("token\tNOUN\n", encoding="utf-8")

        out_file = tmp_path / "cli_out.vrt"
        script_path = os.path.join(os.path.dirname(__file__), "convert_to_xml.py")

        result = subprocess.run(
            [sys.executable, script_path, "-j", str(json_file), "-a", str(annotated_file), "-o", str(out_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert out_file.exists()
        root = ET.fromstring(out_file.read_text(encoding="utf-8"))
        assert root.attrib["video_id"] == "cli_vid"
