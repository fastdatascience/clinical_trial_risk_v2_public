import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("condition")


class TestConditionExtractor(unittest.TestCase):
    # def test_empty(self):
    #     d_result = d.process(document=Document(pages=[]))
    #     self.assertEqual("HIV", d_result["prediction"])

    def test_hiv(self):
        document = Document(pages=[Page(content="this is a hiv trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("HIV", d_result["prediction"])

    def test_tb(self):
        document = Document(pages=[Page(content="this is a tb trial", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("TB", d_result["prediction"])

    def test_cancer(self):
        document = Document(pages=[Page(content="this is a trial for neuroblastoma", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("CANCER", d_result["prediction"])

    def test_annotations_correct_text(self):
        document = Document(pages=[Page(content="this is a trial for cancer", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("cancer", d_result["annotations"][0]["text"])

    def test_annotations_correct_char_indices(self):
        document = Document(pages=[Page(content="this is an hiv trial in the USA", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(11, d_result["annotations"][0]["start_char"])
        self.assertEqual(14, d_result["annotations"][0]["end_char"])


if __name__ == "__main__":
    unittest.main()
