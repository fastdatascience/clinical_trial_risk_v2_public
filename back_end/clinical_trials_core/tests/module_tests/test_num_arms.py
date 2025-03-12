import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("num_arms")


class TestNumArmsExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(2, d_result["prediction"])

    def test_rubbish(self):
        document = Document(pages=[Page(content="blah blah", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(2, d_result["prediction"])

    #
    # def test_simple_num_arms_present_word(self):
    #     document = Document(pages=[Page(content="this study has four experimental arms", page_number=1)])
    #     d_result = d.process(document=document)
    #     self.assertEqual(4, d_result["prediction"])

    def test_simple_num_arms_present_numeric(self):
        document = Document(
            pages=[Page(content="this study has 4 experimental arms", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(4, d_result["prediction"])

    def test_simple_num_arms_present_numeric_short(self):
        document = Document(
            pages=[Page(content="this study has 4 arms", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(4, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
