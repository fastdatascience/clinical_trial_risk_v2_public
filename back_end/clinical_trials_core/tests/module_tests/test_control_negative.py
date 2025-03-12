import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("control_negative")


class TestControlNegative(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="The test-negative design is an increasingly popular approach for estimating vaccine effectiveness (VE) due to its efficiency. This review aims to examine published test-negative design studies of VE and to explore similarities and differences in methodological choices for different diseases and vaccines.",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
