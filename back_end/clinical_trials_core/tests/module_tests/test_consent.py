import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("consent")


class TestConsent(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual("none", d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="Eligible participants will also \nundergo a multi-step consent process.",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        # self.assertEqual("multi step consent", d_result["prediction"]) # TODO: do we care about multi step?
        self.assertEqual("consent", d_result["prediction"])

    def test_implicit(self):
        document = Document(
            pages=[
                Page(
                    content="The consent involves a two-step process consisting of",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual("consent", d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
