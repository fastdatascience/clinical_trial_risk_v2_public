import json
import re

from spacy.matcher import PhraseMatcher
from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.resources import nlp

patterns = dict()

patterns["randomisation"] = ["randomization", "randomizations", "randomize", "randomized", "randomizing", "randomizes"]
patterns["randomisation"].extend([re.sub("z", "s", r) for r in patterns["randomisation"]])

patterns["intra-operative"] = ["intra-operative", "intra-operatively", "intra-op"]
patterns["intra-operative"].extend(
    [re.sub("-", " ", r) for r in patterns["intra-operative"]] + [re.sub("-", "", r) for r in
                                                                  patterns["intra-operative"]])

patterns["crossover"] = []
for r in patterns["randomisation"]:
    patterns["crossover"].extend([f"cross-over {r}", f"cross over {r}", f"crossover {r}",
                                  f"cross-over-{r}", f"cross over-{r}", f"crossover-{r}"])
patterns["cluster"] = ["cluster", "clusters"]

patterns["citations"] = ["et al", "recent study", "recent studies", "previous study", "previous studies"]

context_matcher_names = {"randomisation", "citations"}
randomisation_matcher_names = {"intra-operative", "crossover", "cluster"}

for number_group in [("1", "one", "single"), ("2", "two"), ("3", "three"), ("multi", "multiple")]:
    pattern_key = number_group[0] + " step"
    patterns[pattern_key] = []
    randomisation_matcher_names.add(pattern_key)

    for number in number_group:
        for hyphen in ["-", " ", "", "- ", " - "]:
            for step in ["step", "stage"]:
                patterns[pattern_key].append(f"{number}{hyphen}{step}")

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))


class Randomisation(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="randomisation", name="Randomisation", feature_type="categorical",
                        options=[MetadataOption(label="none", value="none"),
                                 MetadataOption(label="simple", value="simple"),
                                 MetadataOption(label="intra-operative", value="intra-operative"),
                                 MetadataOption(label="cluster", value="cluster"),
                                 MetadataOption(label="crossover", value="crossover"), ])

    def process(self, document: Document, config: ClassifierConfig | None = None):
        candidates = []
        annotations = []
        occurrence_to_pages = {}
        for page_no, doc in enumerate(document.tokenised_pages):
            matches = list(phrase_matcher(doc))

            context_indices = {}
            for context in context_matcher_names:
                context_indices[context] = set()

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]
                if matcher_name in context_matcher_names:
                    context_indices[matcher_name].add(phrase_match[1])
                    context_indices[matcher_name].add(phrase_match[2])

            for phrase_match in matches:
                matcher_name = nlp.vocab.strings[phrase_match[0]]

                if matcher_name in randomisation_matcher_names:
                    distances = {}
                    for context in context_matcher_names:
                        diff = 1000
                        for i in context_indices[context]:
                            diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])
                        distances[context] = diff

                    start = phrase_match[1] - 5
                    if start < 0:
                        start = 0
                    end = phrase_match[2] + 5
                    if end > len(doc):
                        end = len(doc)
                    substr = doc[start:end].text
                    candidate = [matcher_name, distances["randomisation"], distances["citations"],
                                 substr]

                    candidates.append(candidate)

                    match_start_char = doc[phrase_match[1]].idx
                    if phrase_match[2] < len(doc):
                        match_end_char = doc[phrase_match[2]].idx
                    else:
                        match_end_char = len(doc.text)
                    match_text = doc[phrase_match[1]:phrase_match[2]].text
                    annotations.append(
                        {"type": "randomisation", "subtype": matcher_name, "page_no": page_no,
                         "start_char": match_start_char,
                         "end_char": match_end_char, "text": match_text})

                    match_text_norm = match_text.lower()
                    if match_text_norm not in occurrence_to_pages:
                        occurrence_to_pages[match_text_norm] = []
                    occurrence_to_pages[match_text_norm].append(page_no)

        prediction = None
        if len(candidates) > 0:
            for c in candidates:
                if c[2] > 200:
                    if c[0] == "intra-operative" and c[1] > 1:
                        continue
                    if c[0] == "cluster" and c[1] > 10:
                        continue
                    if "step" in c[0] and c[1] > 1:
                        continue
                    prediction = c[0]
                    break

        if prediction == "other" or prediction is None:
            prediction = "none"

        return {"prediction": prediction, "candidates": candidates, "annotations": annotations, "pages": occurrence_to_pages}


if __name__ == "__main__":
    d = Randomisation()
    document = Document(
        pages=[Page(content="subjects were randomized intra-operatively at the end of the index procedure,",
                    page_number=1)])
    d_result = d.process(document=document)
    print(json.dumps(d_result, indent=4))
