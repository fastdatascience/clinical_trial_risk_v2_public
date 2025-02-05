import re

import numpy as np
from spacy.matcher import Matcher, PhraseMatcher

from clinicaltrials.resources import nlp

re_num = re.compile(r'^\d+$')

num_lookup = {"one": 1,
              "two": 2,
              "three": 3,
              "four": 4,
              "five": 5,
              "six": 6,
              "seven": 7,
              "eight": 8,
              "nine": 9,
              "ten": 10,
              "eleven": 11,
              "twelve": 12,
              "thirteen": 13,
              "fourteen": 14,
              "fifteen": 15,
              "sixteen": 16,
              "seventeen": 17,
              "eighteen": 18,
              "nineteen": 19,
              "twenty": 20,
              "twenty-one": 21,
              "twenty-two": 22,
              "twenty-three": 23,
              "twenty-four": 24,
              "twenty-five": 25,
              "twenty-six": 26,
              "twenty-seven": 27,
              "twenty-eight": 28,
              "twenty-nine": 29,
              "thirty": 30,
              "thirty-one": 31,
              "thirty-two": 32,
              "thirty-three": 33,
              "thirty-four": 34,
              "thirty-five": 35,
              "thirty-six": 36,
              "thirty-seven": 37,
              "thirty-eight": 38,
              "thirty-nine": 39,
              "forty": 40,
              "forty-one": 41,
              "forty-two": 42,
              "forty-three": 43,
              "forty-four": 44,
              "forty-five": 45,
              "forty-six": 46,
              "forty-seven": 47,
              "forty-eight": 48,
              "forty-nine": 49,
              "fifty": 50,
              "fifty-one": 51,
              "fifty-two": 52,
              "fifty-three": 53,
              "fifty-four": 54,
              "fifty-five": 55,
              "fifty-six": 56,
              "fifty-seven": 57,
              "fifty-eight": 58,
              "fifty-nine": 59,
              "sixty": 60,
              "sixty-one": 61,
              "sixty-two": 62,
              "sixty-three": 63,
              "sixty-four": 64,
              "sixty-five": 65,
              "sixty-six": 66,
              "sixty-seven": 67,
              "sixty-eight": 68,
              "sixty-nine": 69,
              "seventy": 70,
              "seventy-one": 71,
              "seventy-two": 72,
              "seventy-three": 73,
              "seventy-four": 74,
              "seventy-five": 75,
              "seventy-six": 76,
              "seventy-seven": 77,
              "seventy-eight": 78,
              "seventy-nine": 79,
              "eighty": 80,
              "eighty-one": 81,
              "eighty-two": 82,
              "eighty-three": 83,
              "eighty-four": 84,
              "eighty-five": 85,
              "eighty-six": 86,
              "eighty-seven": 87,
              "eighty-eight": 88,
              "eighty-nine": 89,
              "ninety": 90,
              "ninety-one": 91,
              "ninety-two": 92,
              "ninety-three": 93,
              "ninety-four": 94,
              "ninety-five": 95,
              "ninety-six": 96,
              "ninety-seven": 97,
              "ninety-eight": 98,
              "ninety-nine": 99}

matcher = Matcher(nlp.vocab)

nouns = ['day', 'days', 'duration', 'durations', 'follow', 'follows', 'fu', 'fus', 'month', 'months', 'period',
         'periods', 'week', 'weeks', 'year', 'years', 'follow-up', 'followed-up', 'follow-ups', 'followup', 'followups',
         'visit', 'visits',
         'wk', 'wks', 'yr', 'yrs', 'mth', 'mths'
         ]
noun_word_1 = ["follow", "follows", "followed"]
noun_word_2 = ["up", "ups"]

patterns = []
patterns.append([{"LIKE_NUM": True}, {"LOWER": {"IN": nouns}}])
patterns.append([{"LOWER": {"IN": nouns}}, {"LIKE_NUM": True}])
patterns.append([{"LIKE_NUM": True}, {"LOWER": {"IN": noun_word_1}}, {"LOWER": {"IN": noun_word_2}}])
patterns.append([{"LOWER": {"IN": noun_word_1}}, {"LOWER": {"IN": noun_word_2}}, {"LIKE_NUM": True}])
matcher.add("time", patterns)

patterns = []
patterns.append([{"LOWER": {"IN": ["age", "ages", "aged", "old", "older"]}}])
matcher.add("exclusion", patterns)

phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Takes strings, very fast: https://spacy.io/api/phrasematcher

exclusion_terms = ["years of experience", "years experience"]
phrase_matcher_phrases = list(nlp.pipe(exclusion_terms))
phrase_matcher.add("exclusion", phrase_matcher_phrases)

WINDOW_SIZE = 20


# This function is also called from the training code!
def get_text_snippets_for_nb(docs):
    all_relevant_strings = []
    contexts_this_file = []

    for page_no, doc in enumerate(docs):

        matches = list(matcher(doc))

        matches.extend(phrase_matcher(doc))

        exclude_indices = set()

        for phrase_match in matches:
            matcher_name = nlp.vocab.strings[phrase_match[0]]
            if matcher_name == "exclusion":
                exclude_indices.add(phrase_match[1])
                exclude_indices.add(phrase_match[2])

        for phrase_match in matches:
            matcher_name = nlp.vocab.strings[phrase_match[0]]

            if matcher_name == "time":
                diff = 1000
                for i in exclude_indices:
                    diff = min([diff, abs(i - phrase_match[1]), abs(i - phrase_match[2])])

                if diff > 20:
                    start = phrase_match[1]
                    end = phrase_match[2]

                    context_start = start - WINDOW_SIZE
                    context_end = end + WINDOW_SIZE
                    if context_start < 0:
                        context_start = 0
                    if context_end > len(doc):
                        context_end = len(doc)

                    term = doc[start:end]
                    context = doc[context_start:context_end]

                    time_unit = None
                    for token in term:
                        if token.norm_ in {"day", "days"}:
                            time_unit = "d"
                        elif token.norm_ in {"month", "months", "mth", "mths"}:
                            time_unit = "m"
                        elif token.norm_ in {"year", "years", "yr", "yrs"}:
                            time_unit = "y"
                        elif token.norm_ in {"week", "weeks", "wk", "wks"}:
                            time_unit = "w"

                    normalised_tokens_to_concatenate = []
                    for token in term:
                        normalised_token = token.norm_
                        numeric_value = None

                        if token.like_num and "." in normalised_token:  # if it contains a decimal it's likely to be a chapter number
                            normalised_tokens_to_concatenate = []
                            break

                        if normalised_token == "million":
                            normalised_tokens_to_concatenate = []
                            break

                        if len(re_num.findall(normalised_token)) > 0:
                            numeric_value = int(normalised_token)
                        elif normalised_token in num_lookup:
                            numeric_value = num_lookup[normalised_token]
                            normalised_token = str(numeric_value)
                        if numeric_value is not None:

                            if numeric_value > 1500:  # 4 digit numbers are likely to be dates
                                normalised_tokens_to_concatenate = []
                                break

                            if time_unit == "d" and numeric_value > 365:
                                normalised_token = "365"
                            elif time_unit == "d" and numeric_value > 10:
                                normalised_token = str(int(np.round(numeric_value / 10, 0) * 10))
                            elif time_unit == "m" and numeric_value > 12:
                                normalised_token = "12"
                            elif time_unit == "w" and numeric_value > 52:
                                normalised_token = "52"
                            elif time_unit == "y" and numeric_value > 10:  # anything over 10 years is likely to be age, medical review, etc. Not duration of trial
                                normalised_tokens_to_concatenate = []
                                break

                        normalised_token = re.sub(r's$', '', normalised_token)  # remove plurals

                        normalised_tokens_to_concatenate.append(normalised_token)

                    if len(normalised_tokens_to_concatenate) > 0:
                        all_relevant_strings.append("".join(normalised_tokens_to_concatenate))
                        contexts_this_file.append(re.sub(r'\s+', ' ', context.text))

    return all_relevant_strings, contexts_this_file
