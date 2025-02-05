import bz2
import json
import pickle as pkl
from collections import Counter

from drug_named_entity_recognition import find_drugs

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page


class Drug(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="drug", name="Drug", feature_type="text", )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.model:
            with bz2.open(path_to_classifier, "rb") as f:
                self.model = pkl.load(f)

        model_text, model_reg = self.model
        occurrence_to_pages = {}

        ctr = Counter()
        first_mentions = {}
        contexts = {}
        num_pages = {}
        annotations = []
        for page_no, doc in enumerate(document.tokenised_pages):
            all_matches = find_drugs([t.text for t in doc], is_ignore_case=True)

            matched_tokens = set()
            for d, start, end in all_matches:
                for token_idx in range(start, end + 1):
                    matched_tokens.add(token_idx)

            for d in all_matches:
                drug_name = d[0]["name"]
                ctr[drug_name] += 1
                if drug_name not in first_mentions:
                    first_mentions[drug_name] = page_no
                    contexts[drug_name] = ""
                    num_pages[drug_name] = set()

                num_pages[drug_name].add(page_no)

                start = d[1] - 10
                end = d[2] + 10
                if start < 0: start = 0
                if end > len(doc): end = len(doc)

                for idx in range(start, end):
                    if idx not in matched_tokens:
                        contexts[drug_name] += " " + doc[idx].norm_

                match_start_char = doc[d[1]].idx
                match_end_char = doc[d[2]].idx + len(doc[d[2]].text)
                match_text = doc[d[1]:d[2]].text
                value = d[0]
                annotations.append(
                    {"type": "drug", "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text,
                     "value": value})
                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        ctr = dict(ctr)

        if len(ctr) > 0:
            X_text = []
            X = []
            candidate_names = []

            for drug_name, count in ctr.items():
                candidate_names.append(drug_name)
                X_text.append(contexts[drug_name])
                X.append([count, first_mentions[drug_name], len(num_pages[drug_name]) / len(document.tokenised_pages)])

            y_pred_proba_text = model_text.predict_proba(X_text)
            y_pred_proba = model_reg.predict_proba(X)

            y_pred_proba_ensemble = (y_pred_proba_text + y_pred_proba) / 2

            candidates_with_scores = list(y_pred_proba_ensemble[:, 1])

            candidate_names_and_scores = list(zip(candidate_names, candidates_with_scores))
            prediction = [c[0] for c in candidate_names_and_scores if c[1] > 0.5]
        else:
            prediction = None
            candidate_names_and_scores = []

        return {"prediction": prediction, "counts": ctr, "scores": candidate_names_and_scores,
                "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Drug()
    document = Document(pages=[
        Page(content="Patients in the Axitinib group", page_number=1)])

    d_result = d.process(document=document)

    print(json.dumps(d_result, indent=4))
