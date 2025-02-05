import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("duration")

# short files - duration defaults to 0.25 as common category. TODO: in future refine these tests

class TestDuration(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0.25, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="MRC research laboratories as per study SSP and stored at -70°C or lower in the MRC biobank ",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0.25, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
