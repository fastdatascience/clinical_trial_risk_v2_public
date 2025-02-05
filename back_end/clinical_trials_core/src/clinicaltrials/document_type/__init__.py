import json
import operator
from collections import Counter

from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

patterns = dict()

patterns["protocol"] = ["protocol", "clinical investigation plan", "follow-up plan", "design and outcomes",
                        "study design"]
# patterns["study"] = ["study"]
patterns["development_plan"] = ["development plan", "target product profile"]
patterns["sap"] = ["statistical", "sap"]
patterns["icf"] = ["icf", "consent", "assent"]  # "informed consent form",
phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class DocumentType(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="document_type", name="Document Type", feature_type="categorical",
                        options=[MetadataOption(label="Protocol", value="protocol"),
                                 MetadataOption(label="SAP", value="sap"), MetadataOption(label="ICF", value="icf"),
                                 MetadataOption(label="Development plan", value="development_plan"), ])

    def process(self, document: Document, config: ClassifierConfig | None = None):

        candidates = Counter()
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                candidates[matcher_name] += 1

            if len(candidates) > 0:
                break

        if len(candidates) > 0:
            prediction = list(sorted(candidates.items(), key=operator.itemgetter(1), reverse=True))[0][0]
        else:
            prediction = None

        # if prediction == "study":
        #     prediction = "protocol"

        return {"prediction": prediction, "candidates": candidates}


if __name__ == "__main__":
    d = DocumentType()
    document = Document(
        pages=[Page(
            content="Small Molecule IND Development Plan",
            page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
