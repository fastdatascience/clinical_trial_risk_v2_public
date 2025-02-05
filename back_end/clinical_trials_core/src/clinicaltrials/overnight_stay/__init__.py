import re

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

re_num = re.compile(r"^\d\d?$")

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

patterns["overnight"] = []
for n1 in "overnight over-night hospital".split():
    for n2 in "stay stays".split():
        patterns["overnight"].append(f"{n1} {n2}")
        patterns["overnight"].append(f"{n2} in the {n1}")
        patterns["overnight"].append(f"{n2} in {n1}")

patterns["no overnight"] = [f"no {x}" for x in patterns["overnight"]]

patterns["hospitalize"] = ["hospitalise", "hospitalises", "hospitalised", "hospitalisation", "hospitalisations",
                           "hospitalize", "hospitalizes", "hospitalized", "hospitalization", "hospitalizations"]

patterns["inpatient"] = ["inpatient", "inpatients", "in-patient", "in-patients"]

patterns["ae"] = ["ae", "aes", "sae", "saes", "adverse", "event", "events"]
patterns["exclusion"] = ["exclusion", "exclusions", "excluded", "exclude", "criteria", "criterion"]

context_matcher_names = {"ae", "exclusion"}
phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class OvernightStay(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="overnight_stay", name="Trial involves overnight stay", feature_type="yesno", options=[
            MetadataOption(label="no", value=0),
            MetadataOption(label="yes", value=1),
        ])

    def process(self, document: Document, config: ClassifierConfig | None = None):

        prediction = 0
        annotations = []
        candidates = []
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

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

                if matcher_name not in context_matcher_names:

                    is_definitely_no = 0
                    if matcher_name == "no overnight":
                        is_definitely_no = 1

                    distances = {}
                    for context in context_matcher_names:
                        diff = 1000
                        for i in context_indices[context]:
                            diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])
                        distances[context] = diff

                    start = phrase_match[1] - 40
                    if start < 0:
                        start = 0
                    end = phrase_match[2] + 40
                    if end > len(doc):
                        end = len(doc)
                    substr = doc[start:end].text

                    candidate_value = 1
                    if matcher_name == "overnight":
                        for i in range(phrase_match[1] - 3, phrase_match[2] + 3):
                            if i >= 0 and i < len(doc):
                                if doc[i].norm_ in num_lookup:
                                    candidate_value = num_lookup[doc[i].norm_]
                                elif re_num.match(doc[i].text):
                                    candidate_value = int(doc[i].text)
                    if is_definitely_no:
                        candidate_value = 0

                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    candidates.append(
                        [candidate_value, matcher_name, is_definitely_no, distances["ae"], distances["exclusion"],
                         match_text, substr])

                    annotations.append(
                        {"type": "overnight_stay", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        for cand in candidates:
            if cand[1] != "hospitalize" and cand[3] > 50 and cand[
                4] > 50:  # we must be sufficiently far from any discussion of AEs
                prediction = max([prediction, cand[0]])
        for cand in candidates:
            if cand[2] > 0:  # explicitly no
                prediction = 0

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = OvernightStay()
    document = Document(
        pages=[Page(content="$150.00 for each overnight stay (10 total)", page_number=1)])
    d_result = d.process(document=document)
    print(d_result)
