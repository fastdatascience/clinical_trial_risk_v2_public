import bz2
import json
import pickle as pkl
import re
import time

from spacy.matcher import Matcher, PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.resources import nlp

patterns = dict()

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

patterns["eligibility"] = ["eligibility", "inclusion", "exclusion"]

patterns["age years"] = ["# years old", "# year old", "#-year-old", "# year-old", "age # years", "aged # years",
                         "age: # years", "aged: # years"]

patterns["between years"] = ["# and # years", "# to # years", "#-# years", "# - # years", "# and # year", "# to # year",
                             "#-# year", "# - # year"]

patterns["minimum"] = [">", "at least", "≥"]
patterns["maximum"] = ["<", "to", "under"]
patterns["age"] = ["age", "ages", "aged"]

patterns["years"] = ["# years"]

patterns["citations"] = ["et al", "recent study", "recent studies", "previous study", "previous studies"]

patterns["old"] = ["old", "older"]

patterns["exclusions"] = ["for #", "during #", "within #", "period of #", "every #", "after #",
                          "for a minimum of #", "last #", "past #"]

context_matcher_names = {"citations", "eligibility", "minimum", "maximum", "age", "exclusions", "old"}

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

matcher = Matcher(nlp.vocab)

for feature_name, feature_patterns in patterns.items():

    if "#" not in str(feature_patterns):
        phrase_matcher.add(feature_name, nlp.pipe(feature_patterns))
        continue

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


class Age(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.feature_names = ["x0_lower_value_years", "x1_upper_value_years", "x2_num_values",
                              "x3_distance_to_citations",
                              "x4_distance_to_eligibility",
                              "x5_distance_to_minimum",
                              "x6_distance_to_maximum",
                              "x7_distance_to_age",
                              "x8_distance_to_old",
                              "x9_distance_to_exclusions",
                              ]

        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="age", name="Age", feature_type="numeric_range", )

    def process(self, document: Document, config: ClassifierConfig | None = None):

        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.model:
            with bz2.open(path_to_classifier, "rb") as f:
                self.model = pkl.load(f)

        model_lower, model_upper, model_nb_lower, model_nb_upper = self.model

        annotations = []
        candidates = []  # will be a list of tuples containing data: cohort value, is explicitly mentioning cohort size, distance to mention of cohort
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(matcher(doc)) + list(phrase_matcher(doc))

            context_indices = {}
            for context in context_matcher_names:
                context_indices[context] = set()

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]
                if matcher_name in context_matcher_names:
                    context_indices[matcher_name].add(phrase_match[1])
                    context_indices[matcher_name].add(phrase_match[2])

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                if "years" in matcher_name:

                    is_exclude = False
                    for i in range(phrase_match[1], phrase_match[2]):
                        if i in context_indices["exclusions"]:
                            is_exclude = True
                            break
                    if is_exclude:
                        continue

                    candidate_values = []
                    for i in range(phrase_match[1], phrase_match[2]):
                        if doc[i].like_num and "." not in doc[i].text:
                            if doc[i].norm_ in num_lookup:
                                value = num_lookup[doc[i].norm_]
                            elif re_num.match(doc[i].text):
                                value = int(doc[i].text)
                            else:
                                value = None
                                print("WARNING! NO VALUE FOUND FOR AGE", doc[i].text)
                            if value:
                                candidate_values.append(value)

                    start = phrase_match[1] - 5
                    if start < 0:
                        start = 0
                    end = phrase_match[2] + 5
                    if end > len(doc):
                        end = len(doc)
                    substr = doc[start:end].text

                    distances = {}
                    for context in context_matcher_names:
                        diff = 1000
                        for i in context_indices[context]:
                            diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])
                        distances[context] = diff

                    if len(candidate_values) > 0:
                        v1 = candidate_values[0]
                    else:
                        v1 = 0
                    v2 = 0
                    if len(candidate_values) > 1:
                        v2 = candidate_values[1]

                    if v1 == 0 and v2 == 0:
                        continue
                    candidates.append(
                        [candidate_values, substr, v1, v2, len(candidate_values), distances["citations"],
                         distances["eligibility"],
                         distances["minimum"], distances["maximum"], distances["age"], distances["old"],
                         distances["exclusions"]])

                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    annotations.append(
                        {"type": "age", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text, "value": {"lower": v1, "upper": v2}})
                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        if len(candidates) > 0:
            X = []
            X_text = []
            for c in candidates:
                X.append(c[2:])
                X_text.append(c[1])

            y_pred_proba_lower = model_lower.predict_proba(X)[:, 1]
            y_pred_proba_upper = model_upper.predict_proba(X)[:, 1]

            y_pred_proba_lower_text = model_nb_lower.predict_proba(X_text)[:, 1]
            y_pred_proba_upper_text = model_nb_upper.predict_proba(X_text)[:, 1]

            candidates_with_scores = []
            for idx, candidate in enumerate(candidates):
                candidate_with_scores = list(candidate)
                prob_lower = (y_pred_proba_lower[idx] + y_pred_proba_lower_text[idx]) / 2
                prob_upper = (y_pred_proba_upper[idx] + y_pred_proba_upper_text[idx]) / 2
                candidate_with_scores.append(prob_lower)
                candidate_with_scores.append(prob_upper)
                candidates_with_scores.append(candidate_with_scores)

            candidates_lower = sorted(candidates_with_scores, key=lambda x: x[-2], reverse=True)
            candidates_upper = sorted(candidates_with_scores, key=lambda x: x[-1], reverse=True)

            lower = None
            upper = None
            if len(candidates_lower[0][0]) == 2:
                lower = candidates_lower[0][0][0]
                upper = candidates_lower[0][0][1]
            else:
                if len(candidates_lower[0][0]) > 0:
                    lower = candidates_lower[0][0][0]
                if len(candidates_upper[0][0]) > 0:
                    upper = candidates_upper[0][0][len(candidates_upper[0][0]) - 1
                                                   ]

            if upper == lower:
                if candidates_lower[0][-2] > candidates_upper[0][-1]:
                    upper = None
                else:
                    lower = None

            prediction = {"lower": lower, "upper": upper}
        else:
            prediction = {"lower": None, "upper": None}
            candidates_with_scores = []
        return {"prediction": prediction, "candidates": candidates, "candidates_with_scores": candidates_with_scores,
                "annotations": annotations, "pages": occurrence_to_pages}


#
# if __name__ == "__main__":
#     d = Age()
#     document = Document(
#         pages=[Page(content="Participants were 61 years old, 59% male, 32% non-white, and weighed 97 kg with",
#                     page_number=1)])
#     d_result = d.process(document=document)
#     print(json.dumps(d_result, indent=4))

if __name__ == "__main__":
    d = Age()

    with open("/home/thomas/clinical_trials/data/ctgov/preprocessed_tika/76_NCT02006576_Prot_SAP_000.pdf.pkl",
              "rb") as f:
        pages = pkl.load(f)

    document = Document(
        pages=[Page(content=p,
                    page_number=idx + 1) for idx, p in enumerate(pages)])

    # warm up
    d_result = d.process(document=document)

    start_time = time.time()
    d_result = d.process(document=document)
    end_time = time.time()
    print(json.dumps(d_result, indent=4))

    print(f"Time elapsed: {end_time - start_time:.5f}")
