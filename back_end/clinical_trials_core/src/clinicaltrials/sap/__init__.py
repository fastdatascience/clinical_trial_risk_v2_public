import json
import traceback

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.logs_collector import LogsCollector
from clinicaltrials.resources import nlp
from clinicaltrials.sap.sap_extractor import SapExtractor
from clinicaltrials.sap.sap_extractor_document_level_naive_bayes import SapExtractorDocumentLevel


class Sap(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)
        self.sap_extractor_document_level = None
        self.sap_extractor = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(
            id="sap",
            name="Protocol has Statistical Analysis Plan",
            feature_type="yesno",
            default_weights={"cost": 0.0, "risk": 26.0},
            options=[
                MetadataOption(label="no", value=0),
                MetadataOption(label="yes", value=1),
            ],
        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        logs_collector = LogsCollector()
        config = self.get_classifier_config_or_default(config=config)

        path_to_classifier = config.path_to_classifier

        if not self.sap_extractor_document_level:
            self.sap_extractor_document_level = SapExtractorDocumentLevel(f"{path_to_classifier}/sap_classifier_document_level.pkl.bz2")

            self.sap_extractor = SapExtractor(f"{path_to_classifier}/sap_classifier.pkl.bz2")
        tokenised_pages = [list(nlp(page.content)) for page in document.pages]

        logs_collector.add("Searching for a statistical analysis plan...")
        try:
            sap_to_pages = self.sap_extractor.process(tokenised_pages)
            if sap_to_pages["prediction"] == 1:
                logs_collector.add("It looks like the authors have included their statistical analysis plan in the protocol.")
            elif sap_to_pages["prediction"] == -1:
                logs_collector.add("The machine learning model which detects SAPs was not loaded.")
            else:
                logs_collector.add("It does not look like the protocol contains a statistical analysis plan.")

            logs_collector.add("Testing top pages for SAP with document level SAP Naive Bayes model to refine SAP prediction.")
            sap_to_pages_document_level = self.sap_extractor_document_level.process(tokenised_pages)
            logs_collector.add(
                "Document level Naive Bayes model found SAP score " + str(sap_to_pages_document_level["prediction"]) + " with score " + str(sap_to_pages_document_level["score"])
            )
            sap_to_pages["prediction"] = sap_to_pages_document_level["prediction"]
            sap_to_pages["score"] = float(sap_to_pages_document_level["score"])
        except:
            print(traceback.format_exc())
            logs_collector.add("The tool was unable to identify an SAP. An error occurred.")
            traceback.print_exc()
            sap_to_pages = {"prediction": 0}

        sap_to_pages["logs"] = logs_collector.get()

        return sap_to_pages


if __name__ == "__main__":
    d = Sap()
    document = Document(pages=[Page(content="we will recruit 100 subjects", page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
