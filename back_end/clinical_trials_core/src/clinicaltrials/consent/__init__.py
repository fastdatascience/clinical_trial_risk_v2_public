import json

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

patterns = dict()

consent_pattern_matcher_names = set()
implicit_consent_pattern_matcher_names = set()

for consent_or_assent in ["consent", "assent"]:
    for number_group in [("1", "one", "single"), ("2", "two"), ("3", "three"), ("multi", "multiple")]:
        pattern_key = number_group[0] + " step " + consent_or_assent
        patterns[pattern_key] = []
        consent_pattern_matcher_names.add(pattern_key)

        if consent_or_assent == "consent":
            pattern_key_short = number_group[0] + " step"
            implicit_consent_pattern_matcher_names.add(pattern_key_short)
            patterns[pattern_key_short] = []

        for number in number_group:
            for hyphen in ["-", " ", "", "- ", " - "]:
                for step in ["step", "stage"]:
                    for adj in ["", " informed", " recruitment and", " recruitment and informed"]:
                        patterns[pattern_key].append(f"{number}{hyphen}{step}{adj} {consent_or_assent}")
                    if consent_or_assent == "consent":
                        patterns[pattern_key_short].append(f"{number}{hyphen}{step}")

patterns["citations"] = ["et al", "recent study", "recent studies", "previous study", "previous studies"]
patterns["this study"] = ["this study"]

patterns["consent"] = ["consent"]
patterns["assent"] = ["assent"]

context_matcher_names = {"citations", "this study", "consent", "assent"}

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class Consent(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="consent", name="Consent", feature_type="categorical",
                        options=[MetadataOption(label="none", value="none"),
                                 MetadataOption(label="consent", value="consent"),
                                 MetadataOption(label="assent", value="assent"), ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []
        annotations = []
        occurrence_to_pages = {}

        is_doc_contained_consent = False
        is_doc_contained_assent = False

        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

            for tok in doc:
                if tok.norm_ == "consent":
                    is_doc_contained_consent = True
                if tok.norm_ == "assent":
                    is_doc_contained_assent = True

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

                if matcher_name in consent_pattern_matcher_names.union(implicit_consent_pattern_matcher_names):
                    distances = {}
                    for context in context_matcher_names:
                        diff = 1000
                        for i in context_indices[context]:
                            diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])
                        distances[context] = diff

                    start = phrase_match[1] - 5
                    if start < 0:
                        start = 0
                    end = phrase_match[2] + 5
                    if end > len(doc):
                        end = len(doc)
                    substr = doc[start:end].text

                    is_explicit = int(matcher_name in consent_pattern_matcher_names)

                    candidate = [matcher_name, is_explicit, distances["consent"], distances["assent"],
                                 distances["this study"], distances["citations"], substr]

                    candidates.append(candidate)

                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    annotations.append(
                        {"type": "consent", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        prediction = None
        if len(candidates) > 0:
            for c in candidates:
                if c[5] > 200 and (c[1] == 1 or c[2] < 100 or c[3] < 100):
                    prediction = c[0]
                    if "consent" not in c[0] and "assent" not in c[0]:
                        if c[3] < c[2]:
                            prediction += " assent"
                        else:
                            prediction += " consent"
                    break

        if prediction == "other" or prediction is None:
            prediction = "none"

        if prediction == "none" or " " in prediction:
            if is_doc_contained_assent:
                prediction = "assent"
            elif is_doc_contained_consent:
                prediction = "consent"

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Consent()
    document = Document(
        pages=[Page(
            content="Eligible participants will also \nundergo a multi-step consent process.",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
