import sys
import unittest

from tests import download_and_init_models

sys.path.append("..")
sys.path.append("../src/")

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("country")

download_and_init_models()


class TestCountryExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(["XX"], d_result["prediction"])

    def test_gb(self):
        document = Document(pages=[Page(content="this is a hiv trial in the UK", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(["GB"], d_result["prediction"])

    def test_us(self):
        document = Document(pages=[Page(content="this is a hiv trial in the USA", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(["US"], d_result["prediction"])

    def test_annotations(self):
        document = Document(pages=[Page(content="this is a hiv trial in the USA", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["annotations"][0]["page_no"])

    def test_annotations_correct_page_no(self):
        document = Document(pages=[Page(content="this is a hiv trial in the USA", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["annotations"][0]["page_no"])

    def test_annotations_correct_char_indices(self):
        document = Document(pages=[Page(content="this is a hiv trial in the USA", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(27, d_result["annotations"][0]["start_char"])
        self.assertEqual(30, d_result["annotations"][0]["end_char"])

    def test_annotations_correct_char_indices_demonym(self):
        document = Document(pages=[Page(content="We recruited 100 Zimbabwean women", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(17, d_result["annotations"][0]["start_char"])
        self.assertEqual(33, d_result["annotations"][0]["end_char"])

    def test_annotations_correct_text(self):
        document = Document(pages=[Page(content="We recruited 100 Zimbabwean women", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("Zimbabwean women", d_result["annotations"][0]["text"])


if __name__ == "__main__":
    unittest.main()
