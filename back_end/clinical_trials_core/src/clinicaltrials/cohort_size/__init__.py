import json

from spacy.matcher import Matcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.resources import nlp

word2num = {"one": 1,
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
            "both": 2,
            "single": 2}

cohorts = {"cohort", "cohorts"}
group = {"group", "groups"}

patterns = dict()

patterns["cohort size"] = ["cohort size is #", "cohort size #", "cohort size of #", "cohort size to #",
                           "cohort size increase to #", "cohort size will be #"]

patterns["cohort"] = ["# in cohort", "# per cohort"]

patterns["participants"] = ["# participants", "# patients", "# subjects", "# pts"]

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


class CohortSize(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="cohort_size", name="Cohort Size", feature_type="numeric", )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        annotations = []
        candidates = []  # will be a list of tuples containing data: cohort value, is explicitly mentioning cohort size, distance to mention of cohort
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            page_text = doc.text.lower()
            if "cohort" in page_text or "group" in page_text:
                matches = matcher(doc)

                for phrase_match in matches:
                    matcher_name = nlp.vocab.strings[phrase_match[0]]

                    candidate_value = None
                    for i in range(phrase_match[1], phrase_match[2]):
                        if doc[i].like_num:
                            if doc[i].norm_ in word2num:
                                candidate_value = word2num[doc[i].norm_]
                            elif doc[i].is_digit:
                                candidate_value = int(doc[i].text)

                    if "cohort" in matcher_name:  # explicit mention of cohort size - no other logic needed
                        candidates.append((candidate_value, 1, 0))
                    else:
                        min_dist = 1000
                        start = phrase_match[1] - 10
                        end = phrase_match[2] + 10
                        if start < 0:
                            start = 0
                        if end > len(doc):
                            end = len(doc)

                        for j in range(start, end):
                            if doc[j].norm_ in cohorts:
                                if j < phrase_match[1]:
                                    min_dist = min([abs(j - phrase_match[1]), min_dist])
                                else:
                                    min_dist = min([abs(j - phrase_match[2]), min_dist])

                        if min_dist < 1000:
                            candidates.append((candidate_value, 0, min_dist))

                            match_start_char = doc[phrase_match[1]].idx
                            if phrase_match[2] < len(doc):
                                match_end_char = doc[phrase_match[2]].idx
                            else:
                                match_end_char = len(doc.text)
                            match_text = doc[phrase_match[1]:phrase_match[2]].text
                            annotations.append(
                                {"type": "cohort_size", "subtype": matcher_name, "page_no": page_no,
                                 "start_char": match_start_char,
                                 "end_char": match_end_char, "text": match_text,
                                 "value": {"value": candidate_value}})

                            match_text_norm = match_text.lower()
                            if match_text_norm not in occurrence_to_pages:
                                occurrence_to_pages[match_text_norm] = []
                            occurrence_to_pages[match_text_norm].append(page_no)

        if len(candidates) > 0:
            candidates = sorted(candidates, key=lambda x: x[1] - x[2] / 100, reverse=True)
            prediction = candidates[0][0]
        else:
            prediction = 0
        return {"prediction": prediction, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = CohortSize()
    document = Document(
        pages=[Page(content="The first cohort of 6 patients received drug TID at morning,", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
