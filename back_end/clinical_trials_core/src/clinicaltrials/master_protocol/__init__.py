from spacy.matcher import PhraseMatcher

from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

patterns = dict()

patterns["master_protocol"] = ['basket design', 'basket designs', 'basket extension', 'basket extensions',
                               'basket protocol', 'basket protocols', 'basket studies', 'basket study',
                               'basket sub-studies', 'basket sub-study', 'basket substudies', 'basket substudy',
                               'basket trial', 'basket trials', 'master protocol', 'master protocols',
                               'umbrella design', 'umbrella designs', 'umbrella extension', 'umbrella extensions',
                               'umbrella protocol', 'umbrella protocols', 'umbrella studies', 'umbrella study',
                               'umbrella sub-studies', 'umbrella sub-study', 'umbrella substudies', 'umbrella substudy',
                               'umbrella trial', 'umbrella trials']

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class MasterProtocol(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="master_protocol",
                        name="Trial is a master protocol or a subset or derivative of a master protocol",
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
            if page_no > 3:  # master protocol should be mentioned in the first few pages.
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
                    {"type": "master_protocol", "subtype": matcher_name, "page_no": page_no,
                     "start_char": match_start_char,
                     "end_char": match_end_char, "text": match_text})

        return {"prediction": prediction, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = MasterProtocol()
    document = Document(
        pages=[Page(
            content="This is an open-label, multicenter, phase 1b umbrella study (currently with 3 arms) in patients",
            page_number=1)])

    document = Document(
        pages=[Page(
            content="through a single “umbrella” protocol; therefore, no adjustments for multiplicity are planned.",
            page_number=1)])

    d_result = d.process(document=document)
    print(d_result)
