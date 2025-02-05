import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("randomisation")


class TestRandomisation(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual("none", d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="subjects were randomized intra-operatively at the end of the index procedure,",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("intra-operative", d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
