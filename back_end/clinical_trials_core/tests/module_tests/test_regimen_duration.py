import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("regimen_duration")


class TestRegimenDuration(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual({"until_progression": 0}, d_result["prediction"])

    def test_until_complete_response(self):
        document = Document(
            pages=[
                Page(
                    content="""07_NCT02392507_Prot_000.pdf.txt:The best overall response is the best response recorded from the start of the study treatment until  the earliest of objective progression or start of new anticancer therapy, taking into account any requirement for confirmation.  The patient’s best overall response assignment will depend on the """,
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"]["until_progression"])


if __name__ == "__main__":
    unittest.main()
