import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("child")


class TestChild(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short_child(self):
        document = Document(
            pages=[
                Page(
                    content="weeks premature if less than 2 years of age, infant born",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_short_adult(self):
        document = Document(
            pages=[Page(content="adult males with prostate", page_number=1)]
        )
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
