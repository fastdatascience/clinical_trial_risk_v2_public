import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("human_challenge")


class TestHumanChallenge(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="this is a human challenge study",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
