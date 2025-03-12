import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("effect_estimate")


class TestEffectEstimateExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(pages=[Page(content="blah blah", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_simple_ee_present(self):
        document = Document(
            pages=[
                Page(
                    content="the study will have 80% power to detect a 0.42 log 10 increase in HIV-1 RNA by SCA using a two-sided Wilcoxon rank sum test at 5% level",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
