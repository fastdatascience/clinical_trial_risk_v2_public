import sys

sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial

from clinicaltrials.resources import nlp

ct = ClinicalTrial()

d = ct.get_module("country")

from clinicaltrials.country.phone_number_finder import find_phone_numbers


class TestPhoneNumberFinder(unittest.TestCase):

    def test_empty(self):
        output = find_phone_numbers(nlp("this is a trial trial"))
        self.assertEqual(0, len(output))

    def test_simple_uk(self):
        output = find_phone_numbers(nlp("Please call +44 48415 15445 1")
                                    )
        self.assertEqual(1, len(output))


if __name__ == "__main__":
    unittest.main()
