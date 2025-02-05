from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

patterns = dict()

patterns["platform_trial"] = ['platform design', 'platform designs',
                              'platform protocol', 'platform protocols', 'platform studies', 'platform study',
                              'platform trial', 'platform trials']

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class PlatformTrial(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="master_protocol",
                        name="Trial is part of a platform trial",
                        feature_type="yesno",
                        options=[
                            MetadataOption(label="no", value=0),
                            MetadataOption(label="yes", value=1),
                        ]
                        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        prediction = "no"
        annotations = []
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            if page_no > 3:  # platform trial should be mentioned in the first few pages.
                continue
            matches = list(phrase_matcher(doc))

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                prediction = "yes"

                match_start_char = doc[phrase_match[1]].idx
                if phrase_match[2] < len(doc):
                    match_end_char = doc[phrase_match[2]].idx
                else:
                    match_end_char = len(doc.text)
                match_text = doc[phrase_match[1]:phrase_match[2]].text
                annotations.append(
                    {"type": "platform_trial", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})

                match_text_norm = match_text.lower()
                if match_text_norm not in occurrence_to_pages:
                    occurrence_to_pages[match_text_norm] = []
                occurrence_to_pages[match_text_norm].append(page_no)

        return {"prediction": prediction, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = PlatformTrial()
    document = Document(
        pages=[Page(
            content="Multiple investigational products will be included in this adaptive platform trial. The dose, frequency, ",
            page_number=1)])

    d_result = d.process(document=document)
    print(d_result)
