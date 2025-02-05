import json

from spacy.matcher import PhraseMatcher
from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page, MetadataOption
from clinicaltrials.resources import nlp

patterns = dict()

patterns["explicit"] = ["human challenge study", "human challenge studies", "human challenge trial",
                        "human challenge program", "human challenge programme", "human challenge programs",
                        "human challenge programmes",
                        "human challenge trials", "challenge trial", "challenge trials",
                        "controlled human infection model", "controlled human infection models", "chim", "chims",
                        "challenge virus", "challenge dose", "challenge dosage", "challenge strain"]
patterns["implicit"] = ["human challenge"]

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class HumanChallenge(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="human_challenge", name="Healthy", feature_type="yesno", options=[
            MetadataOption(label="no", value=0),
            MetadataOption(label="yes", value=1),
        ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        """
        Identify if this trial is a human challenge study. https://en.wikipedia.org/wiki/Human_challenge_study
        This is relevant for vaccine trials: we intentionally expose of the test subject to the condition.
        E.g. COVHIC002: "you will be deliberately infected with the COVID-19 virus and carefully monitored until discharge, followed by five follow-up visits over the course of 12 months."
        @param document:
        @param config:
        @return:
        """
        prediction = 0
        annotations = []
        occurrence_to_pages = {}

        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                prediction = 1

                match_start_char = doc[phrase_match[1]].idx
                if phrase_match[2] < len(doc):
                    match_end_char = doc[phrase_match[2]].idx
                else:
                    match_end_char = len(doc.text)
                match_text = doc[phrase_match[1]:phrase_match[2]].text
                annotations.append(
                    {"type": "human_challenge", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})

                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        return {"prediction": prediction, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = HumanChallenge()
    document = Document(
        pages=[Page(
            content="this is a human challenge study",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
