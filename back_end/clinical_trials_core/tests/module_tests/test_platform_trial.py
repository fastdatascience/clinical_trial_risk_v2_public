import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("platform_trial")


class TestPlatformTrial(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual("no", d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="A Phase 2, Multi-center, Multi-arm, Randomized, Placebo-Controlled, Double-Blind, Adaptive Platform Trial to Evaluate the Safety, Tolerability, and Efficacy of Potential Therapeutic Interventions in Active-Duty Service Members and Veterans with Posttraumatic Stress Disorder ",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual("yes", d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
