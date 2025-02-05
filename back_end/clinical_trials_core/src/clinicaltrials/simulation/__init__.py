import bz2
import json
import pickle as pkl

import pandas as pd

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page, MetadataOption
from clinicaltrials.logs_collector import LogsCollector

FEATURE_NAMES = ["simulate-power", "scenarios-power", "simulate-sample", "scenarios-sample", "simulate-sample size", "scenarios-sample size"]


def iterate_tokens(tokenised_pages):
    for page_no, tokens in enumerate(tokenised_pages):
        for token_no, token in enumerate(tokens):
            yield page_no, token_no, token


def extract_features(docs):
    key_words = [
        ["simulate", "simulates", "simulated", "simulating", "simulation", "simulations"],
        ["scenarios"],
        ["power", "powers", "powered", "powering"],
        ["sample", "sampled", "samples", "sampling"],
        ["sample size", ("sample", "size"), ("sample", "sizes")],
    ]

    page_and_token_idx_to_token_idx_in_whole_pdf = {}
    token_idx_in_whole_pdf = 0
    all_tokens = []
    for page_no, doc in enumerate(docs):
        for token in doc:
            page_and_token_idx_to_token_idx_in_whole_pdf[(page_no, token.i)] = token_idx_in_whole_pdf
            token_idx_in_whole_pdf += 1
            all_tokens.append((page_no, token.i, token))

    annotations = []
    token_indexes = {}
    simulation_to_pages = {}
    for key_word_list in key_words:
        canonical = key_word_list[0]
        synonyms = set(key_word_list)
        token_indexes[canonical] = set()
        simulation_to_pages[canonical] = []
        for page_no, doc in enumerate(docs):
            for token in doc:
                if token.norm_ in synonyms:
                    token_idx_in_whole_pdf = page_and_token_idx_to_token_idx_in_whole_pdf[(page_no, token.i)]
                    token_indexes[canonical].add(token_idx_in_whole_pdf)
                    simulation_to_pages[canonical].append(page_no)
                if type(key_word_list[-1]) is tuple and token.i < len(doc) - 1 and (token.norm_, doc[token.i + 1].norm_) in synonyms:
                    token_idx_in_whole_pdf = page_and_token_idx_to_token_idx_in_whole_pdf[(page_no, token.i)]
                    token_indexes[canonical].add(token_idx_in_whole_pdf)
                    simulation_to_pages[canonical].append(page_no)

    feat = []

    contexts = {}

    feature_pages = []

    for feature in FEATURE_NAMES:
        feat1, feat2 = feature.split("-")

        min_dist = -1
        winning_i = None
        winning_j = None
        for i in token_indexes[feat1]:
            for j in token_indexes[feat2]:
                if min_dist == -1 or abs(i - j) < min_dist:
                    min_dist = abs(i - j)
                    winning_i = i
                    winning_j = j

        if min_dist == -1 or min_dist > 1000:
            min_dist = 1000
            page_no = None
        else:
            orig_start_context = min([winning_i, winning_j])
            orig_end_context = max([winning_i, winning_j])
            page_no = all_tokens[winning_i][0]
            contexts[f"Occurrence of “{feat1}” within {min_dist} tokens from “{feat2}”"] = f"Page {page_no + 1}: "

            match_start_char = all_tokens[winning_i][2].idx - 50
            if match_start_char < 0:
                match_start_char = 0
            match_end_char = match_start_char + 50
            if match_end_char > len(doc.text) - 1:
                match_end_char = len(doc.text) - 1
            match_text = doc.text[match_start_char:match_end_char]
            annotations.append({"type": "simulation", "subtype": feature, "page_no": page_no, "start_char": match_start_char, "end_char": match_end_char, "text": match_text})

        feat.append(min_dist)
        feature_pages.append(page_no)

    return feat, simulation_to_pages, contexts, feature_pages, annotations


class Simulation(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)
        self.model = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(
            id="simulation",
            name="Simulation",
            feature_type="yesno",
            options=[
                MetadataOption(label="no", value=0),
                MetadataOption(label="yes", value=1),
            ],
        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        """
        Identify whether the trial uses simulation (e.g. Monte Carlo).

        :return: The prediction (int) and a map to the pages it's mentioned in.
        """

        logs_collector = LogsCollector()
        config = self.get_classifier_config_or_default(config=config)
        path_to_classifier = config.path_to_classifier

        with bz2.open(path_to_classifier, "rb") as f:
            self.model = pkl.load(f)

        # tokenised_pages = [list(nlp(page.content)) for page in document.pages]
        #
        # lc_tokenised_pages = [[tok.norm_ for tok in tokenised_page] for tokenised_page in tokenised_pages]
        #
        # all_tokens = list(iterate_tokens(lc_tokenised_pages))

        feat, simulation_to_pages, contexts, feature_pages, annotations = extract_features(document.tokenised_pages)

        logs_collector.add("Searching for any mentions of simulation...")

        df = pd.DataFrame()
        for feature_idx, feature_name in enumerate(FEATURE_NAMES):
            lst = [feat[feature_idx]]
            for j in range(len(FEATURE_NAMES)):
                if j == feature_idx:
                    lst.append(1000)
                else:
                    lst.append(feat[feature_idx])
            df[feature_name] = lst

        prediction_idx = self.model.predict(df.iloc[0:1])[0]

        if int(prediction_idx) == 1:
            logs_collector.add("The authors probably used simulation for sample size.")
        elif int(prediction_idx) == -1:
            logs_collector.add("The machine learning model which detects the simulation_to_pages was not loaded.")
        else:
            logs_collector.add("It does not look like the authors used simulation for sample size.")

        probabilities = [p[1] for p in self.model.predict_proba(df)]

        probability_of_simulation = probabilities[0]

        # most_informative_feature = np.argmin(probabilities) - 1
        # print ("most_informative_feature", most_informative_feature)

        page_to_probas = [0] * len(document.tokenised_pages)
        for idx, proba in enumerate(probabilities[1:]):
            if feature_pages[idx] is not None:
                page_to_probas[feature_pages[idx]] = float(probabilities[0] - proba)

        ret = {
            "prediction": int(prediction_idx),
            "pages": simulation_to_pages,
            "page_scores": page_to_probas,
            "score": float(probability_of_simulation),
            "context": contexts,
            "annotations": annotations,
        }

        return ret


if __name__ == "__main__":
    d = Simulation()
    document = Document(
        pages=[
            Page(
                content=""" simulate simulates simulated simulating simulation simulations
      scenarios
       power powers powered powering
       sample sampled samples sampling
        sample size    sample size sample sizes  """,
                page_number=1,
            ),
            Page(
                content=""" simulate simulates simulated simulating simulation simulations
      scenarios
       power powers powered powering
       sample sampled samples sampling
        sample size    sample size sample sizes  """,
                page_number=1,
            ),
        ]
    )
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
