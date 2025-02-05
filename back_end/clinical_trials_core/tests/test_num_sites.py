import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("num_sites")


class TestNumSites(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(1, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="between 100 - 200 sites will participate in this glob",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(200, d_result["prediction"])

    def test_one_site(self):
        document = Document(
            pages=[Page(
                content="Clinical Site: The study will be conducted in Tororo, Uganda.",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_threee_sites(self):
        document = Document(
            pages=[Page(
                content="n which 32 communities in three sites in East Africa (two in Uganda and one in Kenya) will be",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(3, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
