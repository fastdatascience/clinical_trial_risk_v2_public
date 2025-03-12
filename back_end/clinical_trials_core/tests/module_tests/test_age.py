import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("age")


class TestAge(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual({"lower": None, "upper": None}, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="Men and women age 30 years or older with symptomatic bilateral",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual({"lower": 30, "upper": None}, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
