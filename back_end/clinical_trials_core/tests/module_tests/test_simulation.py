import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("simulation")


class TestSimulationExtractor(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(pages=[Page(content="blah blah", page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["prediction"])

    def test_simulation_many_keywords_present(self):
        document = Document(
            pages=[
                Page(
                    content=""" simulate simulates simulated simulating simulation simulations
      scenarios
       power powers powered powering
       sample sampled samples sampling
        sample size    sample size sample sizes  """,
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])

    def test_simulation_correct_page_no(self):
        document = Document(
            pages=[
                Page(
                    content=""" simulate simulates simulated simulating simulation simulations
      scenarios
       power powers powered powering
       sample sampled samples sampling
        sample size    sample size sample sizes  """,
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(0, d_result["annotations"][0]["page_no"])

    def test_simulation_correct_annotation_type(self):
        document = Document(
            pages=[
                Page(
                    content=""" simulate simulates simulated simulating simulation simulations
      scenarios
       power powers powered powering
       sample sampled samples sampling
        sample size    sample size sample sizes  """,
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual("simulation", d_result["annotations"][0]["type"])

    def test_simulation_correct_char_indices(self):
        document = Document(
            pages=[
                Page(
                    content=""" simulate simulates simulated simulating simulation simulations
      scenarios
       power powers powered powering
       sample sampled samples sampling
        sample size    sample size sample sizes  """,
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        self.assertEqual(2, d_result["annotations"][0]["start_char"])
        self.assertEqual(52, d_result["annotations"][0]["end_char"])

    # TODO fix this
    # def test_simulation_correct_text(self):
    #     document = Document(pages=[Page(content=""" simulate simulates simulated simulating simulation simulations
    #   scenarios
    #    power powers powered powering
    #    sample sampled samples sampling
    #     sample size    sample size sample sizes  """, page_number=1)])
    #     d_result = d.process(document=document)
    #     self.assertEqual("""simulations scenarios power powers""", d_result["annotations"][0]["text"])


if __name__ == "__main__":
    unittest.main()
