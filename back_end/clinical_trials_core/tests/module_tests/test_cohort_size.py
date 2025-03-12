import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("cohort_size")


class TestCohortSizeExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="The first cohort of 6 patients received drug TID at morning,",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(6, d_result["prediction"])

    def test_simple_num_subjects_present(self):
        document = Document(
            pages=[
                Page(
                    content="Approximately 22 participants will receive daily oral matching placebo and IM 124 in 744LA and 44 in placebo) out of 194 participants (106 in Cohort 1 and 88 will not be formally compared",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(106, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
