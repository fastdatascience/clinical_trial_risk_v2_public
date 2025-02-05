import json

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

cohorts = {"specimen", "specimens", "sample", "samples"}

patterns = dict()

stuff_that_can_be_banked = [
    "antibodies",
    "antibody",
    "bio",
    "bio-fluid",
    "bio-specimen",
    "biofluid",
    "biospecimen",
    "blood",
    "cell",
    "dna",
    "plasma",
    "rna",
    "serum",
    "specimen",
    "stool",
    "tissue",
    "platelet",
    "urine",
    "sample",
    "samples"
]
places_where_it_can_be_stored = ["bank", "banks", "banked", "banking", "repository", "repositories"]
biobank_patterns = []
for thing in stuff_that_can_be_banked:
    for place in places_where_it_can_be_stored:
        biobank_patterns.extend(
            [f"{thing} {place}", f"{thing}{place}", f"{thing}-{place}", f"{thing}s {place}", f"{thing}s-{place}",  f"{place} {thing}",   f"{place} of {thing}", f"{place} for {thing}",
             f"{place} of the {thing}", f"{place} for the {thing}"])

patterns["biobank"] = biobank_patterns

patterns["repository"] = ["repository", "repositories", "banked"]

patterns["negative"] = ["no", "none"]

context_matcher_names = {"negative"}

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class Biobank(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="biobank", name="Biobank", feature_type="yesno",
                        options=[
                            MetadataOption(label="no", value=0),
                            MetadataOption(label="yes", value=1),
                        ]
                        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []  # will be a list of tuples containing data: cohort value, is explicitly mentioning cohort size, distance to mention of cohort
        annotations = []
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = phrase_matcher(doc)

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
                if matcher_name in context_matcher_names:
                    continue

                print ("matcher name = ", matcher_name)

                dist_to_negative = 1000
                for i in context_indices.get("negative", []):
                    dist = abs(i - phrase_match[1])
                    if dist < dist_to_negative:
                        dist_to_negative = dist

                if dist_to_negative < 5:
                    continue

                if matcher_name == "biobank":  # explicit mention of biobank - no other logic needed
                    candidates.append((1, 1, 0))
                else:
                    min_dist = 1000
                    start = phrase_match[1] - 100
                    end = phrase_match[2] + 100
                    if start < 0:
                        start = 0
                    if end > len(doc):
                        end = len(doc)

                    for j in range(start, end):
                        if doc[j].norm_ in stuff_that_can_be_banked:
                            if j < phrase_match[1]:
                                min_dist = min([abs(j - phrase_match[1]), min_dist])
                            else:
                                min_dist = min([abs(j - phrase_match[2]), min_dist])

                    if min_dist < 1000:
                        candidates.append((1, 0, min_dist))

                        match_start_char = doc[phrase_match[1]].idx
                        if phrase_match[2] < len(doc):
                            match_end_char = doc[phrase_match[2]].idx
                        else:
                            match_end_char = len(doc.text)
                        match_text = doc[phrase_match[1]:phrase_match[2]].text
                        annotations.append(
                            {"type": "biobank", "subtype": matcher_name, "page_no": page_no,
                             "start_char": match_start_char,
                             "end_char": match_end_char, "text": match_text})
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
    d = Biobank()
    document = Document(pages=[
        Page(content="A repository is a secure facility that is used to store samples. The Network has a repository in",
             page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
