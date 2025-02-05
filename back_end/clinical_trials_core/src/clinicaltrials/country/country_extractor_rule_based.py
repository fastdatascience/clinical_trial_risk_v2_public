import re

import pycountry

from clinicaltrials.country.country_named_entity_recognition_spacy import find_countries_in_tokens
from clinicaltrials.country.demonym_finder import find_demonyms
from clinicaltrials.country.phone_number_finder import find_phone_numbers

# List of low to medium income countries.
LMIC_COUNTRIES = {"AF",
                  "AL",
                  "AM",
                  "AO",
                  "AR",
                  "AS",
                  "AZ",
                  "BA",
                  "BD",
                  "BF",
                  "BG",
                  "BI",
                  "BJ",
                  "BO",
                  "BR",
                  "BT",
                  "BW",
                  "BY",
                  "BZ",
                  "CF",
                  "CI",
                  "CM",
                  "CN",
                  "CO",
                  "CR",
                  "CU",
                  "CV",
                  "DJ",
                  "DM",
                  "DO",
                  "DZ",
                  "EC",
                  "ER",
                  "ET",
                  "FJ",
                  "GA",
                  "GD",
                  "GE",
                  "GH",
                  "GN",
                  "GQ",
                  "GT",
                  "GW",
                  "GY",
                  "HN",
                  "HT",
                  "ID",
                  "IN",
                  "IQ",
                  "JM",
                  "JO",
                  "KE",
                  "KH",
                  "KI",
                  "KM",
                  "KZ",
                  "LB",
                  "LK",
                  "LR",
                  "LS",
                  "LY",
                  "MA",
                  "MD",
                  "ME",
                  "MG",
                  "MH",
                  "MK",
                  "ML",
                  "MM",
                  "MN",
                  "MR",
                  "MU",
                  "MV",
                  "MW",
                  "MX",
                  "MY",
                  "MZ",
                  "NA",
                  "NE",
                  "NG",
                  "NI",
                  "NP",
                  "PA",
                  "PE",
                  "PG",
                  "PH",
                  "PK",
                  "PY",
                  "RO",
                  "RS",
                  "RU",
                  "RW",
                  "SB",
                  "SD",
                  "SL",
                  "SN",
                  "SO",
                  "SR",
                  "SS",
                  "ST",
                  "SV",
                  "SY",
                  "SZ",
                  "TD",
                  "TG",
                  "TH",
                  "TJ",
                  "TL",
                  "TM",
                  "TN",
                  "TO",
                  "TR",
                  "TV",
                  "TZ",
                  "UA",
                  "UG",
                  "UZ",
                  "VN",
                  "VU",
                  "WS",
                  "ZA",
                  "ZM",
                  "ZW"}

international_regex = re.compile(r"(?i)\b(?:(?:glob|internation|multination)al(?:ly)?|worldwide)\b")

EMAIL_TLDS = {"ad",
              "ae",
              "af",
              "ag",
              "al",
              "am",
              "ao",
              "ar",
              "at",
              "au",
              "az",
              "ba",
              "bb",
              "bd",
              "be",
              "bf",
              "bg",
              "bh",
              "bi",
              "bj",
              "bn",
              "bo",
              "br",
              "bs",
              "bt",
              "bw",
              "by",
              "bz",
              "ca",
              "cd",
              "cf",
              "cg",
              "ch",
              "ci",
              "ck",
              "cl",
              "cm",
              "cn",
              "co",
              "cr",
              "cu",
              "cv",
              "cy",
              "cz",
              "de",
              "dj",
              "dk",
              "dm",
              "do",
              "dz",
              "ec",
              "ee",
              "eg",
              "er",
              "es",
              "et",
              "fi",
              "fj",
              "fm",
              "fr",
              "ga",
              "gb",
              "gd",
              "ge",
              "gh",
              "gm",
              "gn",
              "gq",
              "gr",
              "gt",
              "gw",
              "gy",
              "hn",
              "hr",
              "ht",
              "hu",
              "id",
              "ie",
              "il",
              "in",
              "iq",
              "ir",
              "is",
              "it",
              "jm",
              "jo",
              "jp",
              "ke",
              "kg",
              "kh",
              "ki",
              "km",
              "kn",
              "kp",
              "kr",
              "kw",
              "kz",
              "la",
              "lb",
              "lc",
              "li",
              "lk",
              "lr",
              "ls",
              "lt",
              "lu",
              "lv",
              "ly",
              "ma",
              "mc",
              "md",
              "me",
              "mg",
              "mh",
              "mk",
              "ml",
              "mm",
              "mn",
              "mr",
              "mt",
              "mu",
              "mv",
              "mw",
              "mx",
              "my",
              "mz",
              "na",
              "ne",
              "ng",
              "ni",
              "nl",
              "no",
              "np",
              "nr",
              "nu",
              "nz",
              "om",
              "pa",
              "pe",
              "pg",
              "ph",
              "pk",
              "pl",
              "ps",
              "pt",
              "pw",
              "py",
              "qa",
              "ro",
              "rs",
              "ru",
              "rw",
              "sa",
              "sb",
              "sc",
              "sd",
              "se",
              "sg",
              "si",
              "sk",
              "sl",
              "sm",
              "sn",
              "so",
              "sr",
              "ss",
              "st",
              "sv",
              "sy",
              "td",
              "tg",
              "th",
              "tj",
              "tl",
              "tm",
              "tn",
              "to",
              "tr",
              "tt",
              "tv",
              "tz",
              "ua",
              "ug",
              "us",
              "uy",
              "uz",
              "va",
              "vc",
              "ve",
              "vn",
              "vu",
              "ws",
              "ye",
              "za",
              "zm",
              "zw"}

get_tld_regex = re.compile(r"[a-z]\.(" + "|".join(EMAIL_TLDS) + r")(?:\b|$|/)")


def extract_features(docs: list):
    country_to_pages = {}

    contexts = {}

    annotations = []

    for page_no, doc in enumerate(docs):
        country_matches = find_countries_in_tokens(doc)

        demonym_matches = find_demonyms(doc)

        phone_number_matches = find_phone_numbers(doc)

        all_matches = []
        for country in country_matches:
            all_matches.append((country[0].alpha_2, country[1][1], country[1][2], "country"))
        for demonym in demonym_matches:
            all_matches.append((demonym[0], demonym[1][1], demonym[1][2], "demonym"))
        for phone_number in phone_number_matches:
            all_matches.append((phone_number[0], phone_number[1][1], phone_number[1][2], "phone"))

        for token in doc:
            if token.like_url or token.like_email:
                tld_matches = [m.groups(0) for m in get_tld_regex.finditer(token.text)]
                if len(tld_matches) > 0:
                    tld = tld_matches[0][0]
                    if tld in EMAIL_TLDS:
                        if token.like_url:
                            type = "url"
                        else:
                            type = "email"
                        all_matches.append(
                            (pycountry.countries.lookup(tld).alpha_2, token.i, token.i + 1, type))

        for country_alpha_2, match_start_tok_idx, match_end_tok_idx, match_type in all_matches:
            if country_alpha_2 not in country_to_pages:
                country_to_pages[country_alpha_2] = []

            match_start_char = doc[match_start_tok_idx].idx
            match_end_char = doc[match_end_tok_idx - 1].idx + len(doc[match_end_tok_idx - 1])

            match_text = doc[match_start_tok_idx:match_end_tok_idx].text

            start = match_start_tok_idx - 10
            end = match_end_tok_idx + 10
            if start < 0:
                start = 0
            if end > len(doc) - 1:
                end = len(doc)

            context = doc[start:end].text
            context_clean = re.sub(r'\S+', ' ', context).strip()

            if country_alpha_2 not in contexts:
                contexts[country_alpha_2] = ""
            contexts[country_alpha_2] = contexts[country_alpha_2] + " " + f"Page {page_no + 1}: {context_clean}\n"
            country_to_pages[country_alpha_2].append((page_no, match_type))

            annotations.append(
                {"type": "country", "subtype": match_type, "page_no": page_no, "start_char": match_start_char,
                 "end_char": match_end_char, "text": match_text, "value": {"country_code": country_alpha_2}})

    return country_to_pages, contexts, annotations


class CountryExtractorRuleBased:

    def process(self, docs: list) -> tuple:
        """
        Identify the countries the trial takes place in.

        :param pages: List of string content of each page.
        :return: The prediction (list of strings of Alpha-2 codes) and a map from each country code to the pages it's mentioned in.
        """
        country_to_matches, contexts, annotations = extract_features(docs)

        country_to_pages = {}
        for country, matches in country_to_matches.items():
            country_to_pages[country] = [m for m, t in matches]

        prediction = set()

        if len(country_to_pages) > 0:
            earliest_page = sorted([min(p) for p in country_to_pages.values()])[0]
            for candidate, pages in country_to_pages.items():
                # Any country mentioned on 30+ pages is an investigation country
                unique_pages = set(pages)
                if len(unique_pages) > 30:
                    prediction.add(candidate)
                # Any country mentioned on the first contentful page is also a candidate
                if 0 in unique_pages or earliest_page in unique_pages:
                    prediction.add(candidate)

            first_mentioned_countries = sorted(country_to_pages.items(), key=lambda a: min(a[1]))
            prediction.add(first_mentioned_countries[0][0])

        return {"prediction": list(prediction), "pages": country_to_pages, "features": country_to_matches,
                "context": contexts, "annotations": annotations}
