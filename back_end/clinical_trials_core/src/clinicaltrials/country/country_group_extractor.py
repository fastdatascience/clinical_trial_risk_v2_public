from os.path import exists

import spacy


# Current best model: Expt16
class CountryGroupExtractor:

    def __init__(self, path_to_classifier):
        if not exists(path_to_classifier):
            print(
                f"WARNING! UNABLE TO LOAD COUNTRY GROUP CLASSIFIER {path_to_classifier}. You need to run the training script.")
            self.nlp = None
            return
        self.nlp = spacy.load(path_to_classifier)

    def process(self, tokenised_pages: list) -> tuple:
        """
        Identify whether the trial takes place in US/Canada, LMIC countries, or other.

        :param tokenised_pages: List of lists of tokens of each page.
        :return: The prediction (str): "USCA", "HIGH_INCOME", "LMIC"
        """
        if self.nlp is None:
            print("Warning! Country group classifier not loaded.")
            return {"prediction": "Error"}

        first_10_pages = tokenised_pages[:10]

        combined_tokens = []
        combined_ws = []
        for doc in first_10_pages:
            combined_tokens.extend([t.text for t in doc])
            combined_ws.extend([t.whitespace_ for t in doc])
        doc = spacy.tokens.doc.Doc(self.nlp.vocab, words=combined_tokens, spaces=combined_ws)

        for component_name, component in self.nlp.components:
            if component_name == "textcat":
                component(doc)
        # text = " ".join([doc.text for doc in first_10_pages])
        # doc = self.nlp(text)

        prediction_proba = dict(doc.cats)

        prediction = max(prediction_proba, key=prediction_proba.get)

        return {"prediction": prediction, "pages": {}, "probas": prediction_proba}
