import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("sap")


class TestSapExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(pages=[Page(content="blah blah", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_sap_present(self):
        pages = []
        for i in range(20):
            pages.append(Page(content="center transmission normal content nothing special here", page_number=i))
        for i in range(20):
            pages.append(
                Page(content="pe sap tabulated hazard inferiority statistics maths sample size significance level blah",
                     page_number=i))
        for i in range(20):
            pages.append(Page(content="center transmission normal content nothing special here", page_number=i))
        document = Document(pages=pages)
        d_result = d.process(document=document)
        print(d_result)
        self.assertEqual(0, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
