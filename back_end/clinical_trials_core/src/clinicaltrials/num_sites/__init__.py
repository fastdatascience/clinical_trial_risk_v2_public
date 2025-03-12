import json
import re

import numpy as np
from spacy.matcher import Matcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.resources import nlp

patterns = dict()

places_raw = ["sites", "clinics", "investigational sites", "specialty clinics", "rehabilitation clinics",
              "local clinics",
              "primary care clinics", "outpatient clinics",
              "referral clinics", "locations", "centers", "centres"]
places = []
places.extend(places_raw)
places.extend([f"study {p}" for p in places_raw])
places.extend([f"trial {p}" for p in places_raw])
places.extend([f"investigational {p}" for p in places_raw])
places.extend([f"clinical {p}" for p in places_raw])
places.extend([f"care {p}" for p in places_raw])
places.extend([f"local {p}" for p in places_raw])

patterns["multisite"] = []
for multi in ["multi", "multi ", "multi-", "multiple "]:
    for place in places:
        patterns["multisite"].append(f"{multi}{place}")
        place_singular = re.sub(r"s$", "", place)
        patterns["multisite"].append(f"{multi}{place_singular}")

patterns["singlesite"] = []
for multi in ["single", "single ", "single-", "one "]:
    for place in places:
        patterns["singlesite"].append(f"{multi}{place}")
        place_singular = re.sub(r"s$", "", place)
        patterns["singlesite"].append(f"{multi}{place_singular}")

patterns["num sites"] = []
patterns["implicit"] = []
patterns["very_implicit"] = []
for place in places:
    for variant in ["enrolled at", "recruit at", "we will select", "will include", "plan to include", "settings",
                    "setting", "settings:", "setting:"]:
        patterns["num sites"].append(f"{variant} # {place}")

    for variant in ["will participate"]:
        patterns["num sites"].append(f"# {place} {variant}")

    for variant in ["up to", "approximately", "maximum of"]:
        patterns["implicit"].append(f"{variant} # {place}")

    patterns["very_implicit"].append(f"# {place}")

patterns["phone"] = []
for phone in ["phone", "telephone", "tel", "contact number"]:
    patterns["phone"].extend([f"{phone} #", f"{phone}: #", f"{phone} +#", f"{phone}: +#"])

matcher = Matcher(nlp.vocab)

for feature_name, feature_patterns in patterns.items():
    subpatterns = []
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
            subpatterns.append(pattern)
    matcher.add(feature_name, subpatterns)

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

re_num = re.compile(r"^\d+$")


class NumSites(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="num_sites", name="Number of investigational sites in the trial", feature_type="numeric", is_tertile=True)

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []  # will be a list of tuples containing data: cohort value, is explicitly mentioning cohort size, distance to mention of cohort
        num_mentions_multi_site = 0
        num_mentions_single_site = 0
        num_phone_numbers = 0
        annotations = []
        occurrence_to_pages = {}

        for page_no, doc in enumerate(document.tokenised_pages):

            matches = matcher(doc)

            if "single-site trial" in doc.text:
                print(1)

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                if matcher_name in {"multisite", "singlesite", "phone"}:
                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    annotations.append(
                        {"type": "num_sites", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

                if matcher_name == "multisite":
                    num_mentions_multi_site += 1
                    continue
                elif matcher_name == "singlesite":
                    num_mentions_single_site += 1
                    continue
                elif matcher_name == "phone":
                    num_phone_numbers += 1
                    continue

                candidate_value_text = doc[phrase_match[1]:phrase_match[2]].text.lower()
                candidate_value_numeric = None

                for i in range(phrase_match[1], phrase_match[2]):
                    if doc[i].like_num:
                        if doc[i].norm_ in word2num:
                            candidate_value_numeric = word2num[doc[i].norm_]
                        elif re_num.match(doc[i].norm_):
                            candidate_value_numeric = int(doc[i].text)

                if not candidate_value_numeric:
                    continue

                if matcher_name == "num sites":  # explicit mention of number of sites - no other logic needed
                    candidates.append(
                        [candidate_value_text,
                         candidate_value_numeric,
                         2]
                    )
                elif matcher_name == "implicit":  # implicit mention of number of sites - no other logic needed
                    candidates.append(
                        [candidate_value_text,
                         candidate_value_numeric,
                         1]
                    )
                else:  # very implicit
                    candidates.append(
                        [candidate_value_text,
                         candidate_value_numeric,
                         0]
                    )

                match_start_char = doc[phrase_match[1]].idx
                if phrase_match[2] < len(doc):
                    match_end_char = doc[phrase_match[2]].idx
                else:
                    match_end_char = len(doc.text)
                match_text = doc[phrase_match[1]:phrase_match[2]].text
                annotations.append(
                    {"type": "num_sites", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})

                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        confidence = 0
        if len(candidates) > 0:
            candidates = sorted(candidates, key=lambda x: x[2], reverse=True)
            prediction = candidates[0][1]
            confidence = 0.6
        else:
            # Linear regression model pretrained
            if num_mentions_single_site == 0 and num_mentions_single_site == 0 and num_phone_numbers == 0:
                prediction = 1
                confidence = 0.1
            else:
                prediction = int(np.round(
                    1.81194943 + 2.0255376 * num_mentions_multi_site + -0.31408328 * num_mentions_single_site + 0.04524224 * num_phone_numbers))
                confidence = 0.2
        return {"prediction": prediction, "confidence": confidence, "num_mentions_multi_site": num_mentions_multi_site,
                "num_mentions_single_site": num_mentions_single_site, "candidates": candidates,
                "num_phone_numbers": num_phone_numbers, "annotations": annotations, "pages": occurrence_to_pages}


#
#
# if __name__ == "__main__":
#     d = NumSites()
#     # document = Document(
#     #     pages=[Page(content="between 100 - 200 sites will participate in this glob", page_number=1)])
#     # d_result = d.process(document=document)
#     # print(d_result)
#
#     import os
#     import pickle as pkl
#
#     folder = "/home/thomas/protocols_random_to_test/"
#
#     for file in os.listdir(folder):
#         # if "MAT-V-2018-R-M.pdf.pkl" not in file:
#         #     continue
#         #     if file not in annotations:
#         #         continue
#         # if file in annotations:
#         #     continue
#         if file.endswith("pkl"):
#             print(file)
#             full_file = folder + "/" + file
#             with open(full_file, "rb") as f:
#                 pages = pkl.load(f)
#             document = Document(pages=[
#                 Page(content=p, page_number=page_no) for page_no, p in enumerate(pages)])
#
#             d_result = d.process(document=document)
#             print(json.dumps(d_result, indent=4))
#
#


if __name__ == "__main__":
    d = NumSites()
    import pickle as pkl

    with open("/home/thomas/clinical_trials/data/ctgov/preprocessed_tika/47_NCT02946047_Prot_SAP_000.pdf.pkl",
              "rb") as f:
        pages = pkl.load(f)
    document = Document(
        pages=[Page(
            content=p,
            page_number=i) for i, p in enumerate(pages)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
