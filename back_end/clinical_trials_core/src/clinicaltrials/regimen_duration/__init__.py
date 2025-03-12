from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.resources import nlp

patterns = dict()

patterns["progression_toxicity_death"] = ["progression", "progressions", "toxicity", "death", "metastasis",
                                          "metastatic", "response", "complete response", "cr", "pd", "pds"]
patterns["until"] = ["until", "untill", "til", "till", "up to"]

patterns["context_regimen"] = ["culture", "cultures", "cycle", "cycles", "dosage", "dosages", "dose", "doses", "dosing",
                               "infusion", "infusions", "injection", "injections", "receive", "regimen", "regimens",
                               "treatment", "treatments"]

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Takes strings, very fast: https://spacy.io/api/phrasematcher

for key, terms in patterns.items():
    phrase_matcher_phrases = list(nlp.pipe(terms))
    phrase_matcher.add(key, phrase_matcher_phrases)

context_matcher_names = {"context_regimen", "until"}


class RegimenDuration(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(
            id="regimen_duration",
            name="Regimen duration is open",
            feature_type="multiple_numeric",
            has_multiple_predictions=True,
        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []
        annotations = []
        contexts = []
        prediction = {"until_progression": 0}
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

                distances = {}
                for context in context_matcher_names:
                    diff = 1000
                    for i in context_indices[context]:
                        if context in {"until", "maximum"} and i >= phrase_match[1]:
                            continue  # "until" is always on the left
                        diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])
                    distances[context] = diff

                if matcher_name == "progression_toxicity_death":
                    if distances["until"] < 10 and distances["context_regimen"] < 50:
                        prediction["until_progression"] = 1

                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        return {"prediction": prediction, "candidates": candidates, "contexts": contexts, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = RegimenDuration()
    document = Document(
        pages=[Page(
            content="Each participant will receive pembrolizumab every 21 days for up to 12 month or until confirmed disease progression on MRI or CT, unacceptable toxicity, confirmed.positive pregnancy test or withdrawal of consent.",
            page_number=1)])
    d_result = d.process(document=document)
    print(d_result)
