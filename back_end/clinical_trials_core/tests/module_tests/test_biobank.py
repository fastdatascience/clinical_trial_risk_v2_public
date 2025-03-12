import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("biobank")


class TestBiobank(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="MRC research laboratories as per study SSP and stored at -70°C or lower in the MRC biobank ",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_no_bb(self):
        document = Document(
            pages=[
                Page(
                    content="None of the samples will be retained after the end of the study. No biobank is to be set up. All remaining biological material will be destroyed and the destruction procedure will be recorded in a certificate of destruction.",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_no_bb_2(self):
        document = Document(
            pages=[
                Page(
                    content="None of the samples will be retained after the end of the study. No bank of biological material will be set up. All remaining biological material will be destroyed, and the procedure will be documented with a certificate of destruction.",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_samples_banked(self):
        document = Document(
            pages=[
                Page(
                    content="Samples will be shipped to the DCC where they will be banked and where the biochemical and cellular study-specific analyses will be performed",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_samples_separate_consent(self):
        document = Document(
            pages=[
                Page(
                    content="were reviewed. Banking of blood for genetic studies requires a separate informed consent.  The ",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_plasma_banking(self):
        document = Document(
            pages=[
                Page(
                    content="platelet mitochondria, ascorbate, cardiolipin, plasma banking) ",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
