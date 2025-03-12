import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("sample_size")


class TestSampleSizeExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(pages=[Page(content="blah blah", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_simple_num_subjects_present(self):
        document = Document(
            pages=[Page(content="we will recruit 1000 subjects", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(1000, d_result["prediction"])

    def test_2500(self):
        document = Document(
            pages=[
                Page(content="Target enrollment is 2500 participants", page_number=1)
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(2500, d_result["prediction"])

    def test_exclude_contents_page(self):
        document = Document(
            pages=[
                Page(
                    content="Study population 31 6.1 subject inclusion criteria",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
