import json
import re
import traceback

import numpy as np

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.logs_collector import LogsCollector
from clinicaltrials.phase.phase_extractor_rule_based import PhaseExtractorRuleBased
from clinicaltrials.phase.phase_extractor_spacy import PhaseExtractorSpacy
from clinicaltrials.resources import nlp


class Phase(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.phase_extractor_rule_based = None
        self.phase_extractor_spacy = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="phase", name="Phase", feature_type="categorical",
                        options=[MetadataOption(label="Early Phase 1", value="early_phase_1"),
                                 MetadataOption(label="1", value="1"), MetadataOption(label="1.5", value="1.5"),
                                 MetadataOption(label="2", value="2"), MetadataOption(label="2.5", value="2.5"),
                                 MetadataOption(label="3", value="3"), MetadataOption(label="3.5", value="3.5"),
                                 MetadataOption(label="4", value="4"),
                                 MetadataOption(label="Unknown", value="unknown"), ],
                        default_weights={"cost": 0.0, "risk": 5.0})

    def process(self, document: Document, config: ClassifierConfig | None = None):
        """
        Identify the trial phase.
        :param tokenized_pages: List of lists of tokens of each page.
        :return: The prediction (str) and a map from phase to the pages it's mentioned in.
        """

        logs_collector = LogsCollector()
        config = self.get_classifier_config_or_default(config=config)
        path_to_classifier = config.path_to_classifier

        if not self.phase_extractor_rule_based:
            self.phase_extractor_rule_based = PhaseExtractorRuleBased(
                f"{path_to_classifier}/phase_rf_classifier.pkl.bz2")
            self.phase_extractor_spacy = PhaseExtractorSpacy(f"{path_to_classifier}/spacy-textcat-phase-04-model-best")

        tokenised_pages = [list(nlp(page.content)) for page in document.pages]
        spacy_docs = document.tokenised_pages
        print("Initializing phase random Forest classifier", path_to_classifier)

        logs_collector.add("Searching for a phase...")
        try:
            phase_to_pages = self.phase_extractor_rule_based.process(spacy_docs)
            logs_collector.add(f"This looks like a Phase {phase_to_pages['prediction']} trial.")
        except:
            phase_to_pages = {"prediction": 0}
            logs_collector.add("The tool was unable to identify a trial phase. An error occurred.")
            print(traceback.format_exc())

        try:
            phase_to_pages_spacy = self.phase_extractor_spacy.process(tokenised_pages)
            logs_collector.add(f"Neural network thought it was a Phase {phase_to_pages_spacy['prediction']} trial.")
            combined_scores = {}
            if len(phase_to_pages["probas"]) > 0:
                for phase, score in phase_to_pages["probas"].items():
                    nn_score = phase_to_pages_spacy["probas"].get(phase)
                    if nn_score is not None:
                        combined_scores[phase] = np.mean([float(score), float(nn_score)])
            else:
                combined_scores = phase_to_pages_spacy["probas"]
            phase_to_pages["probas_corrected"] = combined_scores
            phase_to_pages["prediction"] = float(re.sub(r"Phase ", "", max(combined_scores, key=combined_scores.get)))
        except:
            logs_collector.add("Error running neural network model.")

            traceback.print_exc()

        phase_to_pages["logs"] = logs_collector.get()

        return phase_to_pages


if __name__ == "__main__":
    d = Phase()
    document = Document(pages=[Page(content="this is a phase i ii trial", page_number=1)])
    d_result = d.process(document=document)

    print(json.dumps(d_result, indent=4))
