import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("overnight_stay")


class TestOvernightStay(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_no(self):
        document = Document(
            pages=[Page(
                content="There are no overnight stays in the clinic.",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_yes(self):
        document = Document(
            pages=[Page(
                content="Patients with planned overnight stay",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_number(self):
        document = Document(
            pages=[Page(
                content="$150.00 for each overnight stay (10 total)",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(10, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
