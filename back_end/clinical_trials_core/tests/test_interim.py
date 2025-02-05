import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("interim")


class TestInterim(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="ion. Given the relatively small sample sizes, no interim analyses are planned, however data will be assess",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_yes(self):
        document = Document(
            pages=[Page(
                content="ion. Given the relatively small sample sizes, five interim analyses are planned, however data will be assess",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
