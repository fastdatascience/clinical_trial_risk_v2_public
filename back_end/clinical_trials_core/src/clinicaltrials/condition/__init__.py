import bz2
import json
import pickle as pkl

import numpy as np

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page


class Condition(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="condition", name="Condition", feature_type="categorical",
                        options=[MetadataOption(label="HIV", value="HIV"),
                                 MetadataOption(label="Tuberculosis", value="TB"),
                                 MetadataOption(label="COVID", value="COVID"),
                                 MetadataOption(label="Influenza", value="INFLUENZA"),
                                 MetadataOption(label="Malaria", value="MAL"),
                                 MetadataOption(label="Enteric and diarrheal diseases", value="EDD"),
                                 MetadataOption(label="Neglected tropical diseases", value="NTD"),
                                 MetadataOption(label="Polio", value="POL"),
                                 MetadataOption(label="Diabetes", value="DIABETES"),
                                 MetadataOption(label="Pneumonia", value="PNE"),
                                 MetadataOption(label="Other (see full product)", value="other"), ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.model:
            with bz2.open(path_to_classifier, "rb") as f:
                self.model = pkl.load(f)
        vectoriser = self.model.named_steps["countvectorizer"]
        transformer = self.model.named_steps["tfidftransformer"]
        nb = self.model.named_steps["multinomialnb"]
        vocabulary = {v: k for k, v in vectoriser.vocabulary_.items()}

        annotations = []

        tokenised_pages = document.tokenised_pages

        token_counts = np.zeros((1, len(vectoriser.vocabulary_)))
        for tokens in tokenised_pages:
            for token in tokens:
                token_lower = token.norm_
                if token_lower in vectoriser.vocabulary_:
                    token_counts[0, vectoriser.vocabulary_[token_lower]] += 1

        transformed_document = transformer.transform(token_counts)

        prediction_probas = nb.predict_proba(transformed_document)[0]
        prediction_idx = int(np.argmax(prediction_probas))

        prediction = self.model.classes_[prediction_idx]

        probas = np.zeros((transformed_document.shape[1]))
        for i in range(transformed_document.shape[1]):
            zeros = np.zeros(transformed_document.shape)
            zeros[0, i] = transformed_document[0, i]
            proba = nb.predict_log_proba(zeros)
            probas[i] = proba[0, prediction_idx]

        condition_to_pages = {}
        for vocab_idx in np.argsort(-probas):
            condition_to_pages[vocabulary[vocab_idx]] = []
            if len(condition_to_pages) > 20:
                break

        informative_terms = {}
        for vocab_idx in np.argsort(-probas):
            informative_terms[vocabulary[vocab_idx]] = 1
            if len(informative_terms) > 50:
                break

        for page_no, doc in enumerate(tokenised_pages):
            for token in doc:
                if token.norm_ in condition_to_pages:
                    condition_to_pages[token.norm_].append(page_no)

                    match_start_char = token.idx
                    match_end_char = token.idx + len(token.text)
                    match_text = token.text
                    annotations.append(
                        {"type": "condition", "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

        return {"prediction": prediction, "pages": condition_to_pages, "score": prediction_probas[prediction_idx],
                "probas": list(prediction_probas), "terms": informative_terms, "annotations": annotations}


if __name__ == "__main__":
    d = Condition()
    document = Document(pages=[Page(content="this is a phase i ii cancer trial", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
