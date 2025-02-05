import json
import re
import traceback

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, Page
from clinicaltrials.logs_collector import LogsCollector
from clinicaltrials.num_arms.num_arms_extractor import NumArmsExtractor
from clinicaltrials.num_arms.num_arms_extractor_naive_bayes import NumArmsExtractorNaiveBayes
from clinicaltrials.num_arms.num_arms_extractor_spacy import NumArmsExtractorSpacy
from clinicaltrials.resources import nlp


class NumArms(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.num_arms_extractor_nb = None
        self.num_arms_extractor_spacy = None
        self.num_arms_extractor = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="num_arms", name="Number of investigational arms in the trial", feature_type="numeric",
                        default_weights={"cost": 0.0, "risk": 2.0})

    def process(self, document: Document, config: ClassifierConfig | None = None):
        logs_collector = LogsCollector()
        config = self.get_classifier_config_or_default(config=config)
        path_to_classifier = config.path_to_classifier

        if not self.num_arms_extractor_nb:
            self.num_arms_extractor_nb = NumArmsExtractorNaiveBayes(
                f"{path_to_classifier}/arms_classifier_document_level.pkl.bz2")
            self.num_arms_extractor_spacy = NumArmsExtractorSpacy(
                f"{path_to_classifier}/spacy-textcat-arms-21-model-best")
            self.num_arms_extractor = NumArmsExtractor()

        tokenised_pages = [list(nlp(page.content)) for page in document.pages]

        try:
            num_arms_to_pages_nb = self.num_arms_extractor_nb.process(tokenised_pages)
            logs_collector.add(f"Naive Bayes arms prediction probabilities: {num_arms_to_pages_nb['proba']}.")
        except:
            logs_collector.add("Error extracting number of arms!")
            num_arms_to_pages_nb = {"prediction": "2"}
            print(traceback.format_exc())

        try:
            num_arms_to_pages_spacy = self.num_arms_extractor_spacy.process(tokenised_pages)
            logs_collector.add(f"Spacy arms prediction probabilities: {num_arms_to_pages_spacy['proba']}.")
        except:
            logs_collector.add("Error extracting number of arms!")
            num_arms_to_pages_spacy = {"prediction": "2"}
            print(traceback.format_exc())

        combined_arms_probabilities = {}
        for num_arms in ["1", "2", "3+"]:
            combined_arms_probabilities[num_arms] = (num_arms_to_pages_spacy["proba"][num_arms] +
                                                     num_arms_to_pages_nb["proba"][num_arms]) / 2
        most_likely_arms = max(combined_arms_probabilities, key=combined_arms_probabilities.get)

        logs_collector.add("Searching for a number of arms...")
        try:
            num_arms_to_pages = self.num_arms_extractor.process(tokenised_pages, document.tokenised_pages)
            if num_arms_to_pages["prediction"] is not None:
                logs_collector.add(f"It looks like the trial has {num_arms_to_pages['prediction']} arm(s).")

                if most_likely_arms in ("1", "2") and num_arms_to_pages["prediction"] == int(
                    re.sub(r"\+", "", num_arms_to_pages_nb["prediction"])):
                    logs_collector.add("The NB prediction and the rule based prediction match!")
                elif most_likely_arms == "3+" and num_arms_to_pages["prediction"] >= 3:
                    logs_collector.add("The NB prediction and the rule based prediction match by range!")
            else:
                logs_collector.add("No explicit mention of arms found.")
                num_arms_to_pages["prediction"] = int(re.sub(r"\+", "", most_likely_arms))
        except:
            logs_collector.add("Error extracting number of arms!\n")
            traceback.print_exc()
            num_arms_to_pages = {"prediction": 0}
            print(traceback.format_exc())

        num_arms_to_pages["pages"] = num_arms_to_pages["pages"] | num_arms_to_pages_nb["pages"]

        num_arms_to_pages["logs"] = logs_collector.get()

        return num_arms_to_pages


if __name__ == "__main__":
    d = NumArms()
    document = Document(pages=[Page(content="we will recruit for 3 arms", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
