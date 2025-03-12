import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("vaccine")


class TestVaccineExtractor(unittest.TestCase):
    def test_non_vaccine(self):
        document = Document(pages=[Page(content="this is a drug trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_vaccine(self):
        document = Document(
            pages=[Page(content="this is a vaccine trial", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_cancer(self):
        document = Document(
            pages=[Page(content="this is a trial for neuroblastoma", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_annotations_correct_text(self):
        document = Document(
            pages=[Page(content="this is a trial for a vaccine", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual("vaccine", d_result["annotations"][0]["text"])

    def test_annotations_correct_char_indices(self):
        document = Document(
            pages=[Page(content="this is an vaccine trial in the USA", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(11, d_result["annotations"][0]["start_char"])
        self.assertEqual(18, d_result["annotations"][0]["end_char"])


if __name__ == "__main__":
    unittest.main()
