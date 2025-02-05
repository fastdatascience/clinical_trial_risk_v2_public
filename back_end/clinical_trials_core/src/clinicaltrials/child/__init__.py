import bz2
import json
import pickle as pkl

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page, MetadataOption
from clinicaltrials.resources import nlp

cohorts = {"cohort", "cohorts"}
group = {"group", "groups"}

patterns = dict()

patterns["eligibility"] = ["eligibility", "eligible", "inclusion", "exclusion",
                           "criteria", "criterion",
                           "male", "female", "males", "females", "man", "woman", "men", "women", "boy", "girl", "boys",
                           "girls",
                           "gender", "sex", "child", "children", "baby", "babies", "neonate", "neonates", "newborn",
                           "newborns",
                           "infant", "infants",
                           "adolescent", "adolescents", "pediatric", "paediatric", "pediatrics", "paediatrics"]

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class Child(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="child", name="Child", feature_type="yesno", options=[
            MetadataOption(label="no", value=0),
            MetadataOption(label="yes", value=1),
        ])

    def process(self, document: Document, config: ClassifierConfig | None = None):

        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.model:
            with bz2.open(path_to_classifier, "rb") as f:
                self.model = pkl.load(f)

        texts = []
        annotations = []
        occurrence_to_pages = {}

        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]
                start = phrase_match[1] - 20
                end = phrase_match[2] + 20

                if start < 0: start = 0
                if end > len(doc): end = len(doc)

                substr = doc[start:end].text

                texts.append(substr)

                match_start_char = doc[phrase_match[1]].idx
                if phrase_match[2] < len(doc):
                    match_end_char = doc[phrase_match[2]].idx
                else:
                    match_end_char = len(doc.text)
                match_text = doc[phrase_match[1]:phrase_match[2]].text
                annotations.append(
                    {"type": "child", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})
                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        if len(texts) > 0:

            X = [" ".join(texts)]

            y_pred_proba = self.model.predict_proba(X)[0]

            prediction = int(y_pred_proba[1] > 0.5)
            y_pred_proba = list(y_pred_proba)

        else:
            prediction = 0
            y_pred_proba = []

        return {"prediction": prediction,
                "proba": y_pred_proba, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Child()
    document = Document(
        pages=[Page(content="weeks premature if less than 2 years of age, infant born", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
