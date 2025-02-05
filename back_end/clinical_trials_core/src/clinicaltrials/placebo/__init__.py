import bz2
import json
import pickle as pkl

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page, MetadataOption
from clinicaltrials.resources import nlp


class Placebo(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="placebo", name="Trial has placebo arm", feature_type="yesno", options=[
            MetadataOption(label="no", value=0),
            MetadataOption(label="yes", value=1),
        ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.model:
            with bz2.open(path_to_classifier, "rb") as f:
                self.model = pkl.load(f)

        X = []
        ctr = 0
        first_occurrence_page_no = 1000

        occurrence_to_pages = {}

        annotations = []

        for page_no, page in enumerate(document.tokenised_pages):
            doc = nlp(page)
            for tok in doc:
                if tok.lower_ == "placebo":
                    ctr += 1
                    if first_occurrence_page_no == 1000:
                        first_occurrence_page_no = page_no

                    match_start_char = tok.idx
                    match_end_char = tok.idx + len(tok.text)
                    match_text = tok.text
                    annotations.append(
                        {"type": "placebo", "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        X.append([ctr, first_occurrence_page_no])

        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)
        probas_list = list(y_pred_proba[:, 1])

        prediction = int(y_pred[0])

        return {"prediction": prediction, "probas": probas_list, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Placebo()
    document = Document(
        pages=[Page(content="The placebo group of 6 patients received drug TID at morning,", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
