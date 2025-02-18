import nltk
import time
import re
import io
import bz2
import operator
import pickle as pkl
from collections import Counter

from wordcloud import WordCloud
from PIL import Image
from spacy.tokens import Doc

from app import utils

# Download stopwords before importing NLTK stopwords
nltk.download("stopwords", download_dir="/tmp/nltk_data")
nltk.data.path.append("/tmp/nltk_data")

from nltk.corpus import stopwords

# Stopwords
stops = set(stopwords.words("english")).union(set(stopwords.words("french")))
stops.update(
    [
        "protocol",
        "protocols",
        "subject",
        "subjects",
        "trial",
        "trials",
        "doctor",
        "doctors",
        "eg",
        "get",
        "getting",
        "got",
        "gotten",
        "rx",
    ]
)

MAX_NUM_WORDS = 100
WORDCLOUD_TOKEN_REGEX = re.compile(r"(?i)^([a-z][a-z]+)$")


class WordcloudGenerator:
    def __init__(self, classifier_path: str):
        """
        Load the default values of IDF for the words in a training corpus from a Pickle file. This is needed to
        determine the size of the words in the word cloud as words which occur in many protocols are not informative and
        should appear small so the word cloud algorithm is a little different from the standard word cloud algorithm
        which is based on frequency alone.

        :param classifier_path: The path to the Pickle file containing IDFs.
        """

        with bz2.open(classifier_path, "rb") as f:
            self.__idf = pkl.load(f)

    def generate(
        self, tokenised_pages: list[Doc], condition_to_pages: dict
    ) -> dict[str, str]:
        """
        Giving a list of tokenized pages, this function generates a word cloud using Matplotlib and outputs in as base64
        encoded image. Terms which were decisive in the decision of the pathology classifier are displayed in a
        different colour, hence why the condition dictionary is needed.

        :param tokenised_pages: Tokens occurring in the document by page.
        :param condition_to_pages: Needed to identify which terms contributed to the decision of the pathology.
        :returns: A dict response e.g. {"wordcloud_base64": ..., "log": ...}.
        """

        def condition_colour_func(
            word: str,
            font_size: int,
            position: str,
            orientation: str,
            random_state=None,
            **kwargs,
        ) -> str:
            """
            Function to use for generating text colors in the wordcloud.
            """

            if word.lower() in condition_to_pages.get("terms", set()):
                return "#f64e8b"

            return "#323232"

        # Start time
        start_time = time.time()

        tfs = Counter()
        normalised_to_all_surface_forms = {}
        token_page_occurrences = Counter()
        for page_tokens in tokenised_pages:
            unique_tokens_on_page = set()
            for token_idx, token in enumerate(page_tokens):
                token_text = token.text
                if WORDCLOUD_TOKEN_REGEX.match(token_text):
                    tl = token_text.lower()
                    if tl in stops:
                        continue
                    unique_tokens_on_page.add(tl)
                    tfs[tl] += 1
                    if tl not in normalised_to_all_surface_forms:
                        normalised_to_all_surface_forms[tl] = Counter()
                    normalised_to_all_surface_forms[tl][token_text] += 1
            for tl in unique_tokens_on_page:
                token_page_occurrences[tl] += 1

        tf_idf = {}
        for term, tf in tfs.items():
            # Ignore any term that occurs on more than half the pages, these are often rubbish.
            # Unless they are informative terms such as HIV.
            if token_page_occurrences[term] > len(
                tokenised_pages
            ) / 4 and term not in condition_to_pages.get("terms", set()):
                continue
            canonical = sorted(
                normalised_to_all_surface_forms[term].items(),
                key=operator.itemgetter(1),
                reverse=True,
            )[0][0]
            tf_idf[canonical] = tf * self.__idf.get(term, self.__idf.get(""))

        # Sort
        tf_idfs_to_include = sorted(
            tf_idf.items(), key=operator.itemgetter(1), reverse=True
        )

        # Keep up to MAX_NUM_WORDS words
        if len(tf_idfs_to_include) > MAX_NUM_WORDS:
            tf_idfs_to_include = tf_idfs_to_include[:MAX_NUM_WORDS]

        # Wordcloud sizes dict
        wordcloud_sizes: dict[str, int] = {}
        tf_idfs_to_include.reverse()
        for counter, (term, tf_idf) in enumerate(tf_idfs_to_include):
            wordcloud_sizes[term] = counter + 1

        # Generate wordcloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            color_func=condition_colour_func,
        ).generate_from_frequencies(wordcloud_sizes)

        # Wordcloud image buffer
        img = wordcloud.to_array()
        pil_img = Image.fromarray(img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")

        # Encode wordcloud image to base64
        encoded = utils.img_to_base64(buffer.getvalue())

        # End time
        end_time = time.time()

        return {
            "wordcloud_base64": encoded,
            "log": f"Wordcloud generated in {end_time - start_time:.2f} seconds.",
        }
