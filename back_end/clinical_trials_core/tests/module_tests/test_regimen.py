import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("regimen")


class TestRegimen(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        print(d_result["prediction"])
        self.assertEqual(0, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_short(self):
        document = Document(
            pages=[
                Page(
                    content="Each participant will receive pembrolizumab every 21 days for up to 12 month or until confirmed disease progression on MRI or CT, unacceptable toxicity, confirmed.positive pregnancy test or withdrawal of consent.",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(21, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_q4w(self):
        document = Document(
            pages=[
                Page(
                    content="engagement modeling exercise.  The 8100-mg IV Q4W dose, the highest dose level of ",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(28, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_g_day(self):
        document = Document(pages=[Page(content="dose of 5 g/day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_eow(self):
        document = Document(pages=[Page(content="dose of 45 mg EOW", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(14, d_result["prediction"]["days_between_doses"])

    def test_regimen_2_tablets_day(self):
        document = Document(
            pages=[Page(content="dose of 2 tablets/day", page_number=1)]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_g_slash_day(self):
        document = Document(pages=[Page(content="dose of g/day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_ml_day(self):
        document = Document(pages=[Page(content="dose of ml/day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_tablets_day(self):
        document = Document(pages=[Page(content="dose of tablets/day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_dose_day(self):
        document = Document(pages=[Page(content="dose/day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_4_mg_total_day(self):
        document = Document(
            pages=[Page(content="dose of 4 mg total/day", page_number=1)]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_10_mg_monthly(self):
        document = Document(
            pages=[Page(content="dose of  10 mg monthly", page_number=1)]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(30, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_45_mg_monthly(self):
        document = Document(
            pages=[Page(content="dose of 45 mg monthly", page_number=1)]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(30, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_45_mg_eow(self):
        document = Document(pages=[Page(content="dose of  45 mg EOW", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(14, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    # TODO: think about what to do with these
    # def test_regimen_per_cycle(self):
    #     document = Document(
    #         pages=[Page(
    #             content="dose of per cycle",
    #             page_number=1)])
    #     d_result = d.process(document=document)
    #     print(d_result["prediction"])
    #     self.assertEqual(["frequency: 21 day"], d_result["prediction"])
    #
    # def test_regimen_per_visit(self):
    #     document = Document(
    #         pages=[Page(
    #             content="dose of per visit",
    #             page_number=1)])
    #     d_result = d.process(document=document)
    #     print(d_result["prediction"])
    #     self.assertEqual(["frequency: 21 day"], d_result["prediction"])

    def test_regimen_g2w_q4w(self):
        document = Document(
            pages=[Page(content="(Q2W for doses 1—3, Q4W thereafter)", page_number=1)]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(14, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_3x_a_day(self):
        document = Document(pages=[Page(content="dose of 3x a day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1 / 3, d_result["prediction"]["days_between_doses"])
        self.assertEqual(3, d_result["prediction"]["doses_per_day"])
        self.assertEqual(1, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_3_space_x_a_day(self):
        document = Document(pages=[Page(content="dose of 3 x a day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1 / 3, d_result["prediction"]["days_between_doses"])
        self.assertEqual(3, d_result["prediction"]["doses_per_day"])
        self.assertEqual(1, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_weird_multiplication_symbol(self):
        document = Document(pages=[Page(content="cream, 2 × daily; ", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1 / 2, d_result["prediction"]["days_between_doses"])
        self.assertEqual(2, d_result["prediction"]["doses_per_day"])
        self.assertEqual(1, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_decimal(self):
        document = Document(pages=[Page(content="dose of 50.4 g/day", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_twice_a_week(self):
        document = Document(pages=[Page(content="twice a week", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(7, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])

    def test_regimen_every_7_days(self):
        document = Document(pages=[Page(content="dose every 7 days", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(7, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])

    def test_regimen_no_fp(self):
        document = Document(
            pages=[
                Page(
                    content="data lock point: release data minus 2 months. Sponsor contact",
                    page_number=1,
                )
            ]
        )
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(0, d_result["prediction"]["days_between_doses"])
        self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])
        self.assertEqual(0, d_result["prediction"]["doses_per_day"])

    def test_regimen_q4h(self):
        document = Document(pages=[Page(content="2 caps q4h", page_number=1)])
        d_result = d.process(document=document)
        print(d_result["prediction"])
        self.assertEqual(1 / 6, d_result["prediction"]["days_between_doses"])
        self.assertEqual(1, d_result["prediction"]["multiple_doses_per_day"])
        self.assertEqual(6, d_result["prediction"]["doses_per_day"])

    # TODO
    # def test_4_day_regimen(self):
    #     document = Document(
    #         pages=[Page(
    #             content="All participants will receive a 4 day regimen of chemotherapy (clofarabine, cyclophosphamide, and etoposide) followed by an infusion of HLA partially matched family member donor NK cells processed through the use of the investigational CliniMACS device. Interleukin-2 (IL-2) will be given three times per week post-infusion for a minimum of 2 weeks. IL-2 administration will continue until donor NK cells are no longer detectable in the recipient, and, at that time, will be discontinued",
    #             page_number=1)])
    #     d_result = d.process(document=document)
    #     print(d_result["prediction"])
    #     self.assertEqual(7 / 3, d_result["prediction"]["days_between_doses"])
    #     self.assertEqual(0, d_result["prediction"]["multiple_doses_per_day"])
    #     self.assertEqual(0, d_result["prediction"]["doses_per_day"])


if __name__ == "__main__":
    unittest.main()
