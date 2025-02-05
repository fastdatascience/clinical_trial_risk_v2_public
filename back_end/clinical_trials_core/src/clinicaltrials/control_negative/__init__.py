import json

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page, MetadataOption
from clinicaltrials.resources import nlp

patterns = dict()

patterns["control negative"] = ["control negative design", "negative control design", "test negative design",
                                "negative test design",
                                "control-negative design", "negative-control design", "test-negative design",
                                "negative-test design",
                                "control negative study", "negative control study", "test negative study",
                                "negative test study",
                                "control-negative study", "negative-control study", "test-negative study",
                                "negative-test study",
                                "control negative studies", "negative control studies", "test negative studies",
                                "negative test studies",
                                "control-negative studies", "negative-control studies", "test-negative studies",
                                "negative-test studies",
                                "control negative trial", "negative control trial", "test negative trial",
                                "negative test trial",
                                "control-negative trial", "negative-control trial", "test-negative trial",
                                "negative-test trial",
                                "test negative control",
                                "test-negative control",
                                "test negative case control",
                                "test-negative case control",
                                "test-negative-case-control",
                                "tncc",
                                ]
patterns["control negative"].extend([x + "s" for x in patterns["control negative"]])
phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class ControlNegative(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="control_negative", name="Control Negative", feature_type="yesno", options=[
            MetadataOption(label="no", value=0),
            MetadataOption(label="yes", value=1),
        ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []
        annotations = []
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

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
                    {"type": "control_negative", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})

                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        prediction = 0
        if len(candidates) > 0:
            prediction = 1

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = ControlNegative()
    document = Document(
        pages=[Page(
            content="The test-negative design is an increasingly popular approach for estimating vaccine effectiveness (VE) due to its efficiency. This review aims to examine published test-negative design studies of VE and to explore similarities and differences in methodological choices for different diseases and vaccines.",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
