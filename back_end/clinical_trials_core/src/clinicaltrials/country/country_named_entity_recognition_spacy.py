import re

import pycountry
from spacy.matcher import PhraseMatcher

from clinicaltrials.resources import nlp

extra_synonyms = {"VN": {"Vietnam"}, "US": {"USA", "the US", "U.S", "U.S.", "U.S.A."},
                  "CZ": {"Czech Rep", "Czech Republic"},
                  "AE": {"UAE", r"U.A.E."},
                  "KR": {"Korea", "Republic of Korea"}, "KP": {"North Korea", "Democratic People's Republic of Korea"},
                  "CI": {"Ivory Coast", "Cote d'Ivoire", "Cote dIvoire", "Cote Divoire"},
                  "CD": {"Congo, The Democratic Republic", "Congo, Democratic Republic",
                         "Democratic Republic of the Congo",
                         "Democratic Republic of Congo", "DR Congo", "DRC"},
                  "CV": {"Cape Verde"}, "SH": {"St. Helena", "St Helena"},
                  "GB": {"Britain", "United Kingdom", "UK", r"U.K", r"U.K."},
                  "VI": {"Virgin Islands (U.S.)", "Virgin Islands (US)", "Virgin Islands (U.S.A.)",
                         "Virgin Islands (USA)", "U.S. Virgin Islands", "US Virgin Islands", "U.S.A. Virgin Islands",
                         "USA Virgin Islands", "American Virgin Islands"},
                  "RU": {"Russia"}, "VA": {"Holy See"}, "BN": {"Brunei"}, "LA": {"Laos"},
                  "VG": {"British Virgin Islands", "Virgin Islands, British", "Virgin Islands (UK)",
                         "Virgin Islands (British)", "Virgin Islands (Britain)", "Virgin Islands (GB)",
                         "Virgin Islands (UK)", "Virgin Islands (Great Britain)"}, "SY": {"Syria"},
                  "GE": {"Republic of Georgia"},
                  'GM': {'gambia, republic of', 'gambia republic', 'republic of gambia', 'republic of the gambia'},
                  "NL": {"Nerlands"}, "IR": {"Iran"}, "AE": {"UAE", "U.A.E."},
                  "GQ": {"equatorial Guinea", "ecuatorial Guinea", "Equatorial Guinea", "Ecuatorial Guinea",
                         "Guinea equatorial", "Guinea ecuatorial", "Guinea Equatorial", "Guinea Ecuatorial"}
                  }

# A set of key words which indicate Georgia the country if they occur within 3 tokens of a mention of Georgia
georgia_country_terms = {"country", "caucasus", "sakartvelo", "kartvelian", "ossetia", "black sea", "caspian", "idze",
                         "tiflis",
                         "batumi",
                         "kutaisi",
                         "rustavi",
                         "zugdidi",
                         "kobuleti",
                         "khashuri",
                         "samtredia",
                         "senaki",
                         "zestafoni",
                         "marneuli",
                         "telavi",
                         "akhaltsikhe",
                         "ozurgeti",
                         "kaspi",
                         "chiatura",
                         "tsqaltubo",
                         "sagarejo",
                         "gardabani",
                         "borjomi",
                         "tkibuli",
                         "khoni",
                         "bolnisi",
                         "akhalkalaki",
                         "gurjaani",
                         "mtskheta",
                         "kvareli",
                         "akhmeta",
                         "kareli",
                         "lanchkhuti",
                         "tsalenjikha",
                         "dusheti",
                         "sachkhere",
                         "dedoplistsqaro",
                         "lagodekhi",
                         "ninotsminda",
                         "abasha",
                         "tsnori",
                         "terjola",
                         "martvili",
                         "jvari",
                         "khobi",
                         "baghdati",
                         "tetritsqaro",
                         "tsalka",
                         "dmanisi",
                         "ambrolauri",
                         "sighnaghi",
                         "tsageri"}

patterns = {}

alpha_2_to_obj = {}
for country in pycountry.countries:
    alpha_2_to_obj[country.alpha_2] = country
    if country.alpha_2 not in patterns:
        patterns[country.alpha_2] = []

    variants = set()
    variants.add(country.name)
    clean_name = re.sub(r'( \(|,).+$', '', country.name)
    variants.add(clean_name)
    variants.add(re.sub(r"(?i)\band\b", "&", clean_name))
    patterns[country.alpha_2].extend(list(variants))

for country_code, synonyms in extra_synonyms.items():
    if country_code not in patterns:
        patterns[country_code] = []
    for name in synonyms:
        if name not in patterns[country_code]:
            patterns[country_code].append(name)

phrase_matcher = PhraseMatcher(nlp.vocab)
phrase_matcher_lower_case = PhraseMatcher(nlp.vocab, attr="LOWER")
phrase_matcher_georgia = PhraseMatcher(nlp.vocab, attr="LOWER")
phrase_matcher_exclusion = PhraseMatcher(nlp.vocab, attr="LOWER")

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher.add(pattern_name, nlp.pipe(pattern_surface_forms))

for pattern_name, pattern_surface_forms in patterns.items():
    phrase_matcher_lower_case.add(pattern_name, nlp.pipe([x.lower() for x in pattern_surface_forms]))

phrase_matcher_georgia.add("georgia", nlp.pipe(georgia_country_terms))
phrase_matcher_exclusion.add("exclusion", nlp.pipe(["guinea pig", "guinea pigs"]))


def find_countries_in_tokens(doc, is_ignore_case=False, is_georgia_probably_the_country: bool = False):
    country_matches = []

    if is_ignore_case:
        matches = list(phrase_matcher_lower_case(doc))
    else:
        matches = list(phrase_matcher(doc))

    georgia_indices = set()
    if not is_georgia_probably_the_country:
        georgia_matches = list(phrase_matcher_georgia(doc))
        for match in georgia_matches:
            georgia_indices.add(match[1])
            georgia_indices.add(match[2])

    matches = sorted(matches, key=lambda match: match[2] - match[1], reverse=True)

    tokens_already_used = set()

    exclusion_matches = list(phrase_matcher_exclusion(doc))
    for match in exclusion_matches:
        for idx in range(match[1], match[2]):
            tokens_already_used.add(idx)

    for phrase_match in matches:
        is_already_used = False
        for idx in range(phrase_match[1], phrase_match[2]):
            if idx in tokens_already_used:
                is_already_used = True

        if is_already_used:
            continue
        matched_country = nlp.vocab.strings[phrase_match[0]]
        if matched_country == "GE" and not is_georgia_probably_the_country:
            start_idx = phrase_match[1]
            end_idx = phrase_match[2]
            dist = 999999
            for test_idx in georgia_indices:
                dist1 = abs(test_idx - start_idx)
                dist2 = abs(test_idx - end_idx)
                dist = min([dist, dist1, dist2])
            if dist > 3:
                continue

        country_matches.append((alpha_2_to_obj[matched_country], phrase_match))

        for idx in range(phrase_match[1], phrase_match[2]):
            tokens_already_used.add(idx)

    return country_matches
