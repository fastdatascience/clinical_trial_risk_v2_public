import json
import re

from drug_named_entity_recognition import find_drugs
from spacy.matcher import PhraseMatcher, Matcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.resources import nlp

"""
The dosage regimen is a systemized dosage schedule with two variables: (a) the size of each drug dose and (b) the time between consecutive dose administrations.

From:
Essential Pharmacokinetics, 2015
"""

re_num = re.compile(r"^\d+$")

num_lookup = {"one": 1,
              "two": 2,
              "three": 3,
              "four": 4,
              "five": 5,
              "six": 6,
              "seven": 7,
              "eight": 8,
              "nine": 9,
              "ten": 10,
              "eleven": 11,
              "twelve": 12,
              "thirteen": 13,
              "fourteen": 14,
              "fifteen": 15,
              "sixteen": 16,
              "seventeen": 17,
              "eighteen": 18,
              "nineteen": 19,
              "twenty": 20,
              "twenty-one": 21,
              "twenty-two": 22,
              "twenty-three": 23,
              "twenty-four": 24,
              "twenty-five": 25,
              "twenty-six": 26,
              "twenty-seven": 27,
              "twenty-eight": 28,
              "twenty-nine": 29,
              "thirty": 30,
              "thirty-one": 31,
              "thirty-two": 32,
              "thirty-three": 33,
              "thirty-four": 34,
              "thirty-five": 35,
              "thirty-six": 36,
              "thirty-seven": 37,
              "thirty-eight": 38,
              "thirty-nine": 39,
              "forty": 40,
              "forty-one": 41,
              "forty-two": 42,
              "forty-three": 43,
              "forty-four": 44,
              "forty-five": 45,
              "forty-six": 46,
              "forty-seven": 47,
              "forty-eight": 48,
              "forty-nine": 49,
              "fifty": 50,
              "fifty-one": 51,
              "fifty-two": 52,
              "fifty-three": 53,
              "fifty-four": 54,
              "fifty-five": 55,
              "fifty-six": 56,
              "fifty-seven": 57,
              "fifty-eight": 58,
              "fifty-nine": 59,
              "sixty": 60,
              "sixty-one": 61,
              "sixty-two": 62,
              "sixty-three": 63,
              "sixty-four": 64,
              "sixty-five": 65,
              "sixty-six": 66,
              "sixty-seven": 67,
              "sixty-eight": 68,
              "sixty-nine": 69,
              "seventy": 70,
              "seventy-one": 71,
              "seventy-two": 72,
              "seventy-three": 73,
              "seventy-four": 74,
              "seventy-five": 75,
              "seventy-six": 76,
              "seventy-seven": 77,
              "seventy-eight": 78,
              "seventy-nine": 79,
              "eighty": 80,
              "eighty-one": 81,
              "eighty-two": 82,
              "eighty-three": 83,
              "eighty-four": 84,
              "eighty-five": 85,
              "eighty-six": 86,
              "eighty-seven": 87,
              "eighty-eight": 88,
              "eighty-nine": 89,
              "ninety": 90,
              "ninety-one": 91,
              "ninety-two": 92,
              "ninety-three": 93,
              "ninety-four": 94,
              "ninety-five": 95,
              "ninety-six": 96,
              "ninety-seven": 97,
              "ninety-eight": 98,
              "ninety-nine": 99}

patterns = dict()

# Patterns such as "bid" which are well known by pharmacists
# This is for doses that are 1x per day or more frequent than that
for first_letter, how_many in [("o", 1), ("q", 4), ("b", 2), ("t", 3)]:
    for dot in [".", " ", "-", ""]:
        for end in ["d", "id", "i.d", "i.d.", "1d", "1.d", "1.d.", "1d."]:
            if first_letter == "q" and "i" not in end:
                how_many = 1
            dose_code = f"{first_letter}{dot}{end}"
            if dose_code not in {"bid", "did"}:
                pattern_name = f"regimen_specific_{how_many}_1d"
                if pattern_name not in patterns:
                    patterns[pattern_name] = []
                patterns[pattern_name].append(dose_code)

for unit in ["doses", "dose", "tablet", "tablets", "infusion", "infusions", "injection",
             "injections", "treatment", "treatments", "g", "mg", "l", "ml", "caps", "capsule", "capsules", "cap"]:
    patterns["regimen_specific_2_1d"].append(f"{unit} bid")
    patterns["regimen_specific_2_1d"].append(f"{unit} po bid")

# Patterns such as "q4w" which are well known by pharmacists, beginning with q and containing a number
# This is for doses that are 1x per day or less frequent than that
time_periods = {"w": ["week", "weeks", "wk", "w", "ws", "wks", "weekly"],
                "m": ["month", "months", "mo", "mos", "m", "monthly"],
                "d": ["d", "day", "days", "daily"],
                "c": ["cy", "cyc", "cycle", "cycles"],
                "v": ["visit", "visits"],
                "h": ["hour", "hr", "h", "hours", "hrs"]
                }

for dot in [".", " ", "-", ""]:
    for time_period_code, time_periods_group in time_periods.items():
        pattern_name = f"regimen_specific_{1}_1{time_period_code}"
        if pattern_name not in patterns:
            patterns[pattern_name] = []
        for time_period in time_periods_group:
            patterns[pattern_name].append(f"q{dot}{time_period}")

            for number in list(range(1, 10)):
                pattern_name = f"regimen_specific_{1}_{number}{time_period_code}"
                if pattern_name not in patterns:
                    patterns[pattern_name] = []
                patterns[pattern_name].append(f"q{number}{time_period}")
                patterns[pattern_name].append(f"q{number} {time_period}")

patterns["regimen_specific_1_2w"].append("eow")

# begin contexts

patterns["context_regimen"] = ["regimen", "regimens", "treatment", "treatments", "dose", "doses", "dosage", "dosages",
                               "injection", "injections", "cycle", "cycles", "culture", "cultures", "infusion",
                               "infusions"]

# end contexts

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Takes strings, very fast: https://spacy.io/api/phrasematcher

for key, terms in patterns.items():
    phrase_matcher_phrases = list(nlp.pipe(terms))
    phrase_matcher.add(key, phrase_matcher_phrases)

# Dynamic matching
numerator = ["x", "×", "times", "time", "doses", "dose", "tablet", "tablets", "infusion", "infusions", "injection",
             "injections", "treatment", "treatments", "g", "mg", "l", "ml", "once", "twice", "thrice", "caps",
             "capsule", "capsules", "cap"]

matcher = Matcher(nlp.vocab)
matcher_code_to_patterns = {}
for time_period_code, time_periods_group in time_periods.items():

    for num_doses_in_interval in [None] + list(range(1, 20)):
        patterns = []

        for is_number_separate_word in [False, True]:

            if num_doses_in_interval is None:
                matcher_code = f"regimen_specific_1_1{time_period_code}"
            else:
                matcher_code = f"regimen_specific_{num_doses_in_interval}_1{time_period_code}"

            for is_numerator_regex in [False, True]:

                for is_per in [False, True]:
                    for is_total in [False, True]:
                        is_abort_pattern = False
                        pattern = []

                        if is_numerator_regex:
                            if num_doses_in_interval is None:
                                pattern.append(
                                    {"TEXT": {
                                        "REGEX": r"^\d+(?:g|mg|l|ml|mol|mmol|mi|lb|oz|mole|moles|µl|µg|sv|msv)$"}})
                            else:
                                is_abort_pattern = True
                        else:
                            if num_doses_in_interval is not None:
                                if is_number_separate_word:
                                    pattern.append({"LOWER": {"IN": [f"{num_doses_in_interval}"]}})
                                    pattern.append(
                                        {"LOWER": {"IN": [f"x", f"×",
                                                          f"times"]}})
                                else:
                                    pattern.append(
                                        {"LOWER": {"IN": [f"{num_doses_in_interval}x", f"{num_doses_in_interval}×",
                                                          f"{num_doses_in_interval}times"]}})
                            else:
                                if is_number_separate_word:
                                    pattern.append({"LOWER": {"IN": numerator}})
                                else:
                                    is_abort_pattern = True
                        if is_total:
                            pattern.append({"LOWER": {"IN": ["total"]}})
                        if is_per:
                            pattern.append({"LOWER": {"IN": ["/", "per", "every", "each", "a"]}})
                            pattern.append({"LOWER": {"IN": time_periods_group}})
                        else:
                            is_found_adverb = False
                            for adverb in "daily", "weekly", "monthly":
                                if adverb in time_periods_group:
                                    pattern.append({"LOWER": {"IN": [adverb]}})
                                    is_found_adverb = True
                            if not is_found_adverb:
                                is_abort_pattern = True

                        if not is_abort_pattern:
                            patterns.append(pattern)

        if matcher_code not in matcher_code_to_patterns:
            matcher_code_to_patterns[matcher_code] = []
        matcher_code_to_patterns[matcher_code].extend(patterns)

for time_period_code, time_periods_group in time_periods.items():
    matcher_code = f"regimen_specific_1_x{time_period_code}"

    pattern = []
    pattern.append({"LOWER": {"IN": ["every", "each"]}})
    pattern.append({"LIKE_NUM": True})
    pattern.append({"LOWER": {"IN": time_periods_group}})
    patterns.append(pattern)

    if matcher_code not in matcher_code_to_patterns:
        matcher_code_to_patterns[matcher_code] = []
    matcher_code_to_patterns[matcher_code].append(pattern)

for matcher_code, patterns in matcher_code_to_patterns.items():
    matcher.add(matcher_code, patterns)

context_matcher_names = {"drug_name", "context_regimen"}


class Regimen(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="regimen", name="Regimen", feature_type="numeric", )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []
        annotations = []
        contexts = []
        prediction = {"days_between_doses": 0, "multiple_doses_per_day": 0, "doses_per_day": 0}
        occurrence_to_pages = {}

        for page_no, doc in enumerate(document.tokenised_pages):
            candidates_this_page = []

            matches = list(phrase_matcher(doc))

            matches.extend(matcher(doc))

            context_indices = {}
            for context in context_matcher_names:
                context_indices[context] = set()

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]
                if matcher_name in context_matcher_names:
                    context_indices[matcher_name].add(phrase_match[1])
                    context_indices[matcher_name].add(phrase_match[2])

            drug_matches = find_drugs([t.text for t in doc], is_ignore_case=True)
            for d, start, end in drug_matches:
                for token_idx in range(start, end + 1):
                    context_indices["drug_name"].add(token_idx)

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                distances = {}
                for context in context_matcher_names:
                    diff = 1000
                    for i in context_indices[context]:
                        if context in {"until", "maximum"} and i >= phrase_match[1]:
                            continue  # "until" is always on the left
                        diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])
                    distances[context] = diff

                if matcher_name.startswith("regimen_specific"):

                    context_start = phrase_match[1] - 5
                    if context_start < 0:
                        context_start = 0
                    context_end = phrase_match[2] + 5
                    if context_end > len(doc) - 1:
                        context_end = len(doc)

                    print("PM", matcher_name, doc[context_start:context_end])

                    params = matcher_name.split("_")
                    dosage_number = int(params[2])
                    frequency = params[3]
                    if "x" in frequency:
                        value = None
                        for i in range(phrase_match[1], phrase_match[2]):
                            if doc[i].like_num and "." not in doc[i].text:
                                if doc[i].norm_ in num_lookup:
                                    value = num_lookup[doc[i].norm_]
                                elif re_num.match(doc[i].text):
                                    value = int(doc[i].text)

                        if value is None:
                            value = 1
                        frequency = re.sub("x", str(value), frequency)

                    candidates_this_page.append(
                        {"dosage_number": dosage_number, "frequency": frequency, "page_no": page_no,
                         "start_idx": phrase_match[1], "end_idx": phrase_match[2],
                         "distance_to_drug": distances["drug_name"],
                         "distance_to_regimen": distances["context_regimen"]
                         })

                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    annotations.append(
                        {"type": "regimen", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

            candidates_this_page = sorted(candidates_this_page, key=lambda c: c["end_idx"] - c["start_idx"],
                                          reverse=True)
            indices_used = set()
            for candidate in candidates_this_page:
                is_overlapping = False
                for idx in range(candidate["start_idx"], candidate["end_idx"]):
                    if idx in indices_used:
                        is_overlapping = True
                if not is_overlapping:
                    candidates.append(candidate)
                for idx in range(candidate["start_idx"], candidate["end_idx"]):
                    indices_used.add(idx)

        candidates = sorted(candidates, key=lambda c: min([c["distance_to_regimen"], c["distance_to_drug"]]))

        if len(candidates) > 0:
            top_candidate = candidates[0]

            frequency_as_num = int(re.sub('[a-z]+', '', top_candidate['frequency']))

            if "d" in top_candidate["frequency"]:
                prediction["days_between_doses"] = frequency_as_num / top_candidate[
                    "dosage_number"]
                if top_candidate["dosage_number"] > 1:
                    prediction["multiple_doses_per_day"] = 1
                if frequency_as_num == 1:
                    prediction["doses_per_day"] = top_candidate["dosage_number"]

            elif "w" in top_candidate["frequency"]:
                prediction["days_between_doses"] = frequency_as_num * 7
            elif "m" in top_candidate["frequency"]:
                prediction["days_between_doses"] = frequency_as_num * 30
            elif "h" in top_candidate["frequency"]:
                prediction["days_between_doses"] = frequency_as_num / 24
                prediction["multiple_doses_per_day"] = 1
                prediction["doses_per_day"] = 24 / frequency_as_num

        return {"prediction": prediction, "candidates": candidates, "contexts": contexts, "annotations": annotations,
                "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Regimen()
    # document = Document(
    #     pages=[Page(
    #         content="Each participant will receive pembrolizumab every 21 days for up to 12 month or until confirmed disease progression on MRI or CT, unacceptable toxicity, confirmed.positive pregnancy test or withdrawal of consent.",
    #         page_number=1)])

    document = Document(
        pages=[Page(
            content="will be given three times per week post-infusion",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
