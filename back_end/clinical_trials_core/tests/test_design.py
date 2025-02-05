import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("design")


class TestDesign(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual("other", d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="This is a 4-period, crossover study in healthy, adults in which 12 participants each received 4 treatments (Treatments A, B, C, and D) randomized in a balanced, crossover design in Periods 1 through 4.",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("crossover", d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
