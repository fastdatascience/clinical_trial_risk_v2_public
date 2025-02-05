import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("phase")


class TestPhaseExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0.5, d_result["prediction"])

    def test_simple_phase_i_present(self):
        document = Document(pages=[Page(content="this is a phase i trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_simple_phase_i_ii_present(self):
        document = Document(pages=[Page(content="this is a phase i ii trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1.5, d_result["prediction"])
        self.assertDictEqual({"Phase 1.5": [0]}, d_result["pages"])

    def test_viral_decay(self):
        document = Document(pages=[Page(content="this is a phase i viral decay", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1.0, d_result["prediction"])
        self.assertDictEqual({}, d_result["pages"])

    def test_annotations_correct_char_indices(self):
        document = Document(pages=[Page(content="this is a phase i ii trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(10, d_result["annotations"][0]["start_char"])
        self.assertEqual(26, d_result["annotations"][0]["end_char"])

    def test_annotations_correct_text(self):
        document = Document(pages=[Page(content="this is a phase i ii trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("phase i ii", d_result["annotations"][0]["text"])


if __name__ == "__main__":
    unittest.main()
