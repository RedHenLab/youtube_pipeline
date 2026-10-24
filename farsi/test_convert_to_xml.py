# -*- coding: utf-8 -*-
import json
import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from farsi.convert_to_xml import convert_to_xml, extract_video_id, xmlescape_mysql


class TestConvertToXML(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.json_path = os.path.join(self.test_dir, "sample.info.json")
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump({
                "id": "Ckr5G4EvEdU",
                "title": "Sample Title",
                "uploader": "TestUploader",
                "upload_date": "20230705",
                "duration": 120
            }, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_xmlescape_mysql(self):
        escaped = xmlescape_mysql('Special & "quotes" <tag> \'single\'')
        self.assertIn('&amp;', escaped)
        self.assertIn('&quot;', escaped)
        self.assertIn('&lt;', escaped)
        self.assertIn('&gt;', escaped)
        self.assertIn('&apos;', escaped)

    def test_extract_video_id(self):
        # 1. Explicit ID
        self.assertEqual(extract_video_id("output.vrt", {"id": "YT123"}, explicit_id="CUSTOM_ID"), "CUSTOM_ID")
        # 2. From JSON when stem is generic 'output'
        self.assertEqual(extract_video_id("output.vrt", {"id": "YT123"}), "YT123")
        # 3. From non-generic stem when JSON has no id
        self.assertEqual(extract_video_id("my_video_123.vrt", {}), "my_video_123")

    def test_plain_vrt_without_sent_id(self):
        """Input without comment lines should auto-open <s> and produce well-formed XML."""
        vrt_input = os.path.join(self.test_dir, "output.vrt")
        with open(vrt_input, "w", encoding="utf-8") as f:
            f.write("لحظه\tN_SING\tلحظه\tNOUN\n")
            f.write("رسید\tV_PA\tرسید\tVERB\n")

        output_vrt = os.path.join(self.test_dir, "result.vrt")
        convert_to_xml(self.json_path, vrt_input, output_vrt)

        self.assertTrue(os.path.exists(output_vrt))
        with open(output_vrt, "r", encoding="utf-8") as f:
            content = f.read()

        # Check video ID derivation from JSON
        self.assertIn('video_id="Ckr5G4EvEdU"', content)
        self.assertIn('id="y__Ckr5G4EvEdU"', content)

        # Check XML parses without ParseError
        root = ET.fromstring(content)
        self.assertEqual(root.tag, "text")
        sentences = root.findall("s")
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0].attrib.get("id"), "1")
        self.assertIn("لحظه", sentences[0].text)

    def test_conllu_with_sent_ids(self):
        """Input with # sent_id = 1 and # sent_id = 2 should have matching <s> tags."""
        conllu_input = os.path.join(self.test_dir, "annotated.conllu")
        with open(conllu_input, "w", encoding="utf-8") as f:
            f.write("# sent_id = 1\n")
            f.write("# text = First sentence.\n")
            f.write("WordOne\tNOUN\n")
            f.write("# sent_id = 2\n")
            f.write("# text = Second sentence.\n")
            f.write("WordTwo\tVERB\n")

        output_vrt = os.path.join(self.test_dir, "result_conllu.vrt")
        convert_to_xml(self.json_path, conllu_input, output_vrt)

        with open(output_vrt, "r", encoding="utf-8") as f:
            content = f.read()

        root = ET.fromstring(content)
        sentences = root.findall("s")
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0].attrib.get("id"), "1")
        self.assertEqual(sentences[1].attrib.get("id"), "2")

    def test_real_sample_file_validation(self):
        """Validates conversion on the repository's bundled sample files."""
        sample_json = "farsi/output_files/Ckr5G4EvEdU.info.json"
        sample_vrt = "farsi/output_files/output.vrt"

        if os.path.exists(sample_json) and os.path.exists(sample_vrt):
            output_vrt = os.path.join(self.test_dir, "real_corpus.vrt")
            convert_to_xml(sample_json, sample_vrt, output_vrt)

            with open(output_vrt, "r", encoding="utf-8") as f:
                content = f.read()

            # Must be valid XML parseable by ElementTree
            root = ET.fromstring(content)
            self.assertEqual(root.tag, "text")
            self.assertEqual(root.attrib.get("video_id"), "Ckr5G4EvEdU")
            sentences = root.findall("s")
            self.assertGreaterEqual(len(sentences), 1)


if __name__ == "__main__":
    unittest.main()
