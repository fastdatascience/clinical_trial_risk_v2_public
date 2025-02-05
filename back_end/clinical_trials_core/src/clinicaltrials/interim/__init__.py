import json
import re
from collections import Counter

from spacy.matcher import Matcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page, MetadataOption
from clinicaltrials.resources import nlp

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

interim_patterns = [f"interim {noun}" for noun in "analysis analyses review reviews".split()]

patterns["no_interim"] = [f"no {i}" for i in interim_patterns]
patterns["no_interim"].extend([f"no formal {i}" for i in interim_patterns])
patterns["no_interim"].extend([f"no planned {i}" for i in interim_patterns])

patterns["interim"] = [f"# {i}" for i in interim_patterns]
patterns["interim"].extend([f"the {i}" for i in interim_patterns])
patterns["interim"].extend([f"the planned {i}" for i in interim_patterns])
patterns["interim"].extend([f"an {i}" for i in interim_patterns])
patterns["interim"].extend([f"first {i}" for i in interim_patterns])
patterns["interim"].extend([f"second {i}" for i in interim_patterns])

context_matcher_names = {"no_interim"}
interim_matcher_names = {"interimn"}

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


class Interim(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="interim", name="Trial has interim review", feature_type="yesno", options=[
            MetadataOption(label="no", value=0),
            MetadataOption(label="yes", value=1),
        ])

    def process(self, document: Document, config: ClassifierConfig | None = None):

        annotations = []
        candidates = []
        occurrence_to_pages = {}
        counter = Counter()
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(matcher(doc))

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]
                counter[matcher_name] += 1

                start = phrase_match[1] - 5
                if start < 0:
                    start = 0
                end = phrase_match[2] + 5
                if end > len(doc):
                    end = len(doc)
                substr = doc[start:end].text
                candidate = [matcher_name, substr]

                candidates.append(candidate)

                match_start_char = doc[phrase_match[1]].idx
                if phrase_match[2] < len(doc):
                    match_end_char = doc[phrase_match[2]].idx
                else:
                    match_end_char = len(doc.text)
                match_text = doc[phrase_match[1]:phrase_match[2]].text
                annotations.append(
                    {"type": "interim", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})

                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        prediction = 0
        if counter.get("no_interim", 0) > 0:
            prediction = 0
        elif counter.get("interim", 0) > 0:
            prediction = 1

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Interim()
    document = Document(
        pages=[Page(
            content="ion. Given the relatively small sample sizes, no interim analyses are planned, however data will be assess",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
