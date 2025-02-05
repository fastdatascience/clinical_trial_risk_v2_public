import json

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

patterns = dict()

patterns["crossover"] = ["crossover", "cross-over"]

patterns["adaptive"] = ["adaptive design"]

patterns["factorial"] = ["factorial"]  # , "# x #", "2x2", "3x3", "3x2", "2x3", "2 x k", "2 x n"]

patterns["other"] = ["sequential", "parallel", "single group"]

patterns["weak_context"] = ["assign", "assigned", "assigns", "assignment"]

patterns["design"] = ["design"]

patterns["citations"] = ["et al", "recent study"]

context_matcher_names = {"design", "citations", "weak_context"}
design_pattern_matcher_names = {"crossover", "factorial", "other", "adaptive"}

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class Design(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="design", name="Design", feature_type="categorical",
                        options=[MetadataOption(label="crossover", value="crossover"),
                                 MetadataOption(label="factorial", value="factorial"),
                                 MetadataOption(label="adaptive", value="adaptive"),
                                 MetadataOption(label="other", value="other"), ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []
        annotations = []
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

                if matcher_name in design_pattern_matcher_names:
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
                    candidate = [matcher_name, distances["design"], distances["citations"], distances["weak_context"],
                                 substr]

                    candidates.append(candidate)

                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    annotations.append(
                        {"type": "design", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})
                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        prediction = None
        if len(candidates) > 0:
            for c in candidates:
                if c[0] in design_pattern_matcher_names and c[2] > 200:
                    prediction = c[0]
                    break

        if prediction == "other" or prediction is None:
            prediction = "other"

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Design()
    document = Document(
        pages=[Page(
            content="This is a 4-period, crossover study in healthy, adults in which 12 participants each received 4 treatments (Treatments A, B, C, and D) randomized in a balanced, crossover design in Periods 1 through 4.",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
