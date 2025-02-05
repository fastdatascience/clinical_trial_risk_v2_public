import bz2
import json
import re

import numpy as np
from spacy.matcher import Matcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.duration.duration_nb import get_text_snippets_for_nb
from clinicaltrials.resources import nlp

import pickle as pkl

patterns = dict()

patterns["time"] = []

for unit in ("day", "month", "week", "year"):
    patterns["time"].extend([f"# {unit}", f"# {unit}s"])

patterns["study duration"] = []
for thing in ["study", "trial", "follow-up", "follow up",
              "subject participation", "treatment", "regimen"]:
    for plural in ["", "s"]:
        things = thing + plural
        patterns["study duration"].extend([f"{things} duration", f"duration of {things}", f"duration of the {things}"])
patterns["study duration"].extend(["will be followed for"])

patterns["age"] = ["age", "ages", "aged", "old", "older", "young", "younger"]

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

matcher = Matcher(nlp.vocab)

for feature_name, feature_patterns in patterns.items():
    patterns = []
    for feature_pattern in feature_patterns:
        for is_range in [0, 1, 2, 3]:
            pattern = []
            for token in nlp(feature_pattern):
                word = token.lower_
                if word == "#":
                    if is_range == 2:
                        pattern.append({"LOWER": {"IN": ["=", ">", "≥", "approx", "approximately", "planned"]}})
                    elif is_range == 3:
                        pattern.append({"LOWER": "up"})
                        pattern.append({"LOWER": "to"})
                    pattern.append({"LIKE_NUM": True})
                    if is_range == 1:
                        pattern.append({"LOWER": {"IN": ["-", "–", "to"]}})
                        pattern.append({"LIKE_NUM": True})
                elif word == "%":  # percentage
                    pattern.append({"TEXT": {"REGEX": r"^\d+%$"}})
                elif word == "*":  # wildcard
                    pattern.append({"LIKE_NUM": False})
                else:
                    pattern.append({"LOWER": word})
            patterns.append(pattern)
    matcher.add(feature_name, patterns)

re_num = re.compile(r"^\d+$")


class Duration(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="duration", name="Duration in years", feature_type="numeric", )

    def process(self, document: Document, config: ClassifierConfig | None = None):

        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.model:
            with bz2.open(path_to_classifier, "rb") as f:
                self.model = pkl.load(f)

        candidates = []  # will be a list of tuples containing data: cohort value, distance to mention of duration, distance to mention of human age
        annotations = []
        occurrence_to_pages = {}

        for page_no, doc in enumerate(document.tokenised_pages):
            matches = matcher(doc)

            duration_token_indices = set()
            age_token_indices = set()

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]
                if matcher_name == "study duration":
                    duration_token_indices.add(phrase_match[1])
                    duration_token_indices.add(phrase_match[2])
                elif matcher_name == "age":
                    age_token_indices.add(phrase_match[1])
                    age_token_indices.add(phrase_match[2])

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                if matcher_name == "time":
                    candidate_value_numeric = None
                    for i in range(phrase_match[1], phrase_match[2]):
                        if doc[i].like_num:
                            if doc[i].norm_ in num_lookup:
                                candidate_value_numeric = num_lookup[doc[i].norm_]
                            elif re_num.match(doc[i].norm_):
                                candidate_value_numeric = int(doc[i].text)
                            else:
                                continue
                    if not candidate_value_numeric:
                        continue
                    candidate_value_text = doc[phrase_match[1]:phrase_match[2]].text.lower()
                    unit = None
                    unit_idx = 0
                    for unit_idx, unit in enumerate(["day", "week", "month", "year"]):
                        if unit in candidate_value_text:
                            break
                    if unit == "day":
                        candidate_value_years = candidate_value_numeric / 365
                    elif unit == "week":
                        candidate_value_years = candidate_value_numeric / 52
                    elif unit == "month":
                        candidate_value_years = candidate_value_numeric / 12
                    elif unit == "year":
                        candidate_value_years = candidate_value_numeric
                    else:
                        candidate_value_years = None

                    min_dist = 1000
                    min_dist_age = 1000
                    start = phrase_match[1] - 10
                    end = phrase_match[2] + 10
                    if start < 0:
                        start = 0
                    if end > len(doc):
                        end = len(doc)

                    for j in range(start, end):
                        if j in duration_token_indices:
                            if j < phrase_match[1]:
                                min_dist = min([abs(j - phrase_match[1]), min_dist])
                            else:
                                min_dist = min([abs(j - phrase_match[2]), min_dist])
                        if j in age_token_indices:
                            if j < phrase_match[1]:
                                min_dist_age = min([abs(j - phrase_match[1]), min_dist_age])
                            else:
                                min_dist_age = min([abs(j - phrase_match[2]), min_dist_age])

                    if min_dist < 1000 and candidate_value_years is not None:
                        candidates.append(
                            [candidate_value_text, candidate_value_years, unit_idx, min_dist, min_dist_age,
                             candidate_value_numeric])

                        match_start_char = doc[phrase_match[1]].idx
                        if phrase_match[2] < len(doc):
                            match_end_char = doc[phrase_match[2]].idx
                        else:
                            match_end_char = len(doc.text)
                        match_text = doc[phrase_match[1]:phrase_match[2]].text
                        annotations.append(
                            {"type": "duration", "subtype": matcher_name, "page_no": page_no,
                             "start_char": match_start_char,
                             "end_char": match_end_char, "text": match_text,
                             "value": {"text": candidate_value_text, "numeric": candidate_value_numeric,
                                       "years": candidate_value_years, "unit": unit}})

                        match_text_norm = match_text.lower()
                        if match_text_norm not in occurrence_to_pages:
                            occurrence_to_pages[match_text_norm] = []
                        occurrence_to_pages[match_text_norm].append(page_no)

        all_relevant_strings, contexts_this_file = get_text_snippets_for_nb(document.tokenised_pages)
        input_for_nb = " ".join(all_relevant_strings)
        nb_prediction = self.model.predict([input_for_nb])[0]
        nb_prediction_conf = self.model.predict_proba([input_for_nb])[0]

        if len(candidates) > 0:
            candidates = sorted(candidates, key=lambda x: x[1] * 0.87718219
                                                          + x[2] * -0.19705639
                                                          + x[3] * -0.04138449
                                                          + x[4] * 0.01149629
                                ,
                                reverse=True)
            prediction = candidates[0][1]
            is_low_confidence = 0
            score = 0.6
        else:
            # If the duration was not found by the rule-based approach, we fall back to Naive Bayes.
            # Translate the categories from Naive Bayes back into years.
            if nb_prediction == 0:
                prediction = 0.25
            elif nb_prediction == 1:
                prediction = 0.5
            elif nb_prediction == 2:
                prediction = 1
            elif nb_prediction == 3:
                prediction = 4
            else:
                prediction = 6
            is_low_confidence = 1

            score = max([0.4, np.max(nb_prediction_conf)])

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations,
                "is_low_confidence": is_low_confidence, "score": score, "pages": occurrence_to_pages}


if __name__ == "__main__":
    # TODO: fix duration in this file - it's coming back as 0

    d = Duration()

    with open("/home/thomas/clinical_trials/data/ctgov/preprocessed_tika/76_NCT02006576_Prot_SAP_000.pdf.pkl",
              "rb") as f:
        pages = pkl.load(f)

    document = Document(
        pages=[Page(content=p,
                    page_number=idx + 1) for idx, p in enumerate(pages)])

    # document = Document(pages=[
    #     Page(content="Study Duration 5 years", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
