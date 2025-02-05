import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("intervention_type")


class TestInterventionType(unittest.TestCase):

    def test_short(self):
        document = Document(
            pages=[Page(
                content="trial of remdesivir a drug trial ",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual("drug", d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
