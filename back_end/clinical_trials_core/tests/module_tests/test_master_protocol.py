import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("master_protocol")


class TestMasterProtocol(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual("no", d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="of the two master protocols described above. Through a simple and generally applicable ",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual("yes", d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
