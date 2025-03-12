import json
import time

from clinicaltrials import model_store
from clinicaltrials.core import BaseProcessor, ClassifierConfig, Document, Metadata, MetadataOption, Page
from clinicaltrials.country.country_ensemble_extractor import CountryEnsembleExtractor
from clinicaltrials.country.country_extractor_rule_based import CountryExtractorRuleBased
from clinicaltrials.country.country_group_extractor import CountryGroupExtractor
from clinicaltrials.country.international_extractor_naive_bayes import InternationalExtractorNaiveBayes
from clinicaltrials.country.international_extractor_spacy import InternationalExtractorSpacy
from clinicaltrials.logs_collector import LogsCollector

country_extractor_rule_based = CountryExtractorRuleBased()


class Country(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

        self.country_group_extractor = None
        self.international_extractor = None
        self.international_extractor_nb = None
        self.country_ensemble_extractor = None

    @property
    def metadata(self) -> Metadata:
        return Metadata(
            id="country",
            name="Country",
            feature_type="multi_label",
            options=[
                MetadataOption(label="Aruba", value="AW"),
                MetadataOption(label="Afghanistan", value="AF"),
                MetadataOption(label="Angola", value="AO"),
                MetadataOption(label="Anguilla", value="AI"),
                MetadataOption(label="Åland Islands", value="AX"),
                MetadataOption(label="Albania", value="AL"),
                MetadataOption(label="Andorra", value="AD"),
                MetadataOption(label="United Arab Emirates", value="AE"),
                MetadataOption(label="Argentina", value="AR"),
                MetadataOption(label="Armenia", value="AM"),
                MetadataOption(label="American Samoa", value="AS"),
                MetadataOption(label="Antarctica", value="AQ"),
                MetadataOption(label="French Southern Territories", value="TF"),
                MetadataOption(label="Antigua and Barbuda", value="AG"),
                MetadataOption(label="Australia", value="AU"),
                MetadataOption(label="Austria", value="AT"),
                MetadataOption(label="Azerbaijan", value="AZ"),
                MetadataOption(label="Burundi", value="BI"),
                MetadataOption(label="Belgium", value="BE"),
                MetadataOption(label="Benin", value="BJ"),
                MetadataOption(label="Bonaire, Sint Eustatius and Saba", value="BQ"),
                MetadataOption(label="Burkina Faso", value="BF"),
                MetadataOption(label="Bangladesh", value="BD"),
                MetadataOption(label="Bulgaria", value="BG"),
                MetadataOption(label="Bahrain", value="BH"),
                MetadataOption(label="Bahamas", value="BS"),
                MetadataOption(label="Bosnia and Herzegovina", value="BA"),
                MetadataOption(label="Saint Barthélemy", value="BL"),
                MetadataOption(label="Belarus", value="BY"),
                MetadataOption(label="Belize", value="BZ"),
                MetadataOption(label="Bermuda", value="BM"),
                MetadataOption(label="Bolivia, Plurinational State of", value="BO"),
                MetadataOption(label="Brazil", value="BR"),
                MetadataOption(label="Barbados", value="BB"),
                MetadataOption(label="Brunei Darussalam", value="BN"),
                MetadataOption(label="Bhutan", value="BT"),
                MetadataOption(label="Bouvet Island", value="BV"),
                MetadataOption(label="Botswana", value="BW"),
                MetadataOption(label="Central African Republic", value="CF"),
                MetadataOption(label="Canada", value="CA"),
                MetadataOption(label="Cocos (Keeling) Islands", value="CC"),
                MetadataOption(label="Switzerland", value="CH"),
                MetadataOption(label="Chile", value="CL"),
                MetadataOption(label="China", value="CN"),
                MetadataOption(label="Côte d'Ivoire", value="CI"),
                MetadataOption(label="Cameroon", value="CM"),
                MetadataOption(label="Congo, The Democratic Republic of the", value="CD"),
                MetadataOption(label="Congo", value="CG"),
                MetadataOption(label="Cook Islands", value="CK"),
                MetadataOption(label="Colombia", value="CO"),
                MetadataOption(label="Comoros", value="KM"),
                MetadataOption(label="Cabo Verde", value="CV"),
                MetadataOption(label="Costa Rica", value="CR"),
                MetadataOption(label="Cuba", value="CU"),
                MetadataOption(label="Curaçao", value="CW"),
                MetadataOption(label="Christmas Island", value="CX"),
                MetadataOption(label="Cayman Islands", value="KY"),
                MetadataOption(label="Cyprus", value="CY"),
                MetadataOption(label="Czechia", value="CZ"),
                MetadataOption(label="Germany", value="DE"),
                MetadataOption(label="Djibouti", value="DJ"),
                MetadataOption(label="Dominica", value="DM"),
                MetadataOption(label="Denmark", value="DK"),
                MetadataOption(label="Dominican Republic", value="DO"),
                MetadataOption(label="Algeria", value="DZ"),
                MetadataOption(label="Ecuador", value="EC"),
                MetadataOption(label="Egypt", value="EG"),
                MetadataOption(label="Eritrea", value="ER"),
                MetadataOption(label="Western Sahara", value="EH"),
                MetadataOption(label="Spain", value="ES"),
                MetadataOption(label="Estonia", value="EE"),
                MetadataOption(label="Ethiopia", value="ET"),
                MetadataOption(label="Finland", value="FI"),
                MetadataOption(label="Fiji", value="FJ"),
                MetadataOption(label="Falkland Islands (Malvinas)", value="FK"),
                MetadataOption(label="France", value="FR"),
                MetadataOption(label="Faroe Islands", value="FO"),
                MetadataOption(label="Micronesia, Federated States of", value="FM"),
                MetadataOption(label="Gabon", value="GA"),
                MetadataOption(label="United Kingdom", value="GB"),
                MetadataOption(label="Georgia", value="GE"),
                MetadataOption(label="Guernsey", value="GG"),
                MetadataOption(label="Ghana", value="GH"),
                MetadataOption(label="Gibraltar", value="GI"),
                MetadataOption(label="Guinea", value="GN"),
                MetadataOption(label="Guadeloupe", value="GP"),
                MetadataOption(label="Gambia", value="GM"),
                MetadataOption(label="Guinea-Bissau", value="GW"),
                MetadataOption(label="Equatorial Guinea", value="GQ"),
                MetadataOption(label="Greece", value="GR"),
                MetadataOption(label="Grenada", value="GD"),
                MetadataOption(label="Greenland", value="GL"),
                MetadataOption(label="Guatemala", value="GT"),
                MetadataOption(label="French Guiana", value="GF"),
                MetadataOption(label="Guam", value="GU"),
                MetadataOption(label="Guyana", value="GY"),
                MetadataOption(label="Hong Kong", value="HK"),
                MetadataOption(label="Heard Island and McDonald Islands", value="HM"),
                MetadataOption(label="Honduras", value="HN"),
                MetadataOption(label="Croatia", value="HR"),
                MetadataOption(label="Haiti", value="HT"),
                MetadataOption(label="Hungary", value="HU"),
                MetadataOption(label="Indonesia", value="ID"),
                MetadataOption(label="Isle of Man", value="IM"),
                MetadataOption(label="India", value="IN"),
                MetadataOption(label="British Indian Ocean Territory", value="IO"),
                MetadataOption(label="Ireland", value="IE"),
                MetadataOption(label="Iran, Islamic Republic of", value="IR"),
                MetadataOption(label="Iraq", value="IQ"),
                MetadataOption(label="Iceland", value="IS"),
                MetadataOption(label="Israel", value="IL"),
                MetadataOption(label="Italy", value="IT"),
                MetadataOption(label="Jamaica", value="JM"),
                MetadataOption(label="Jersey", value="JE"),
                MetadataOption(label="Jordan", value="JO"),
                MetadataOption(label="Japan", value="JP"),
                MetadataOption(label="Kazakhstan", value="KZ"),
                MetadataOption(label="Kenya", value="KE"),
                MetadataOption(label="Kyrgyzstan", value="KG"),
                MetadataOption(label="Cambodia", value="KH"),
                MetadataOption(label="Kiribati", value="KI"),
                MetadataOption(label="Saint Kitts and Nevis", value="KN"),
                MetadataOption(label="Korea, Republic of", value="KR"),
                MetadataOption(label="Kuwait", value="KW"),
                MetadataOption(label="Lao People's Democratic Republic", value="LA"),
                MetadataOption(label="Lebanon", value="LB"),
                MetadataOption(label="Liberia", value="LR"),
                MetadataOption(label="Libya", value="LY"),
                MetadataOption(label="Saint Lucia", value="LC"),
                MetadataOption(label="Liechtenstein", value="LI"),
                MetadataOption(label="Sri Lanka", value="LK"),
                MetadataOption(label="Lesotho", value="LS"),
                MetadataOption(label="Lithuania", value="LT"),
                MetadataOption(label="Luxembourg", value="LU"),
                MetadataOption(label="Latvia", value="LV"),
                MetadataOption(label="Macao", value="MO"),
                MetadataOption(label="Saint Martin (French part)", value="MF"),
                MetadataOption(label="Morocco", value="MA"),
                MetadataOption(label="Monaco", value="MC"),
                MetadataOption(label="Moldova, Republic of", value="MD"),
                MetadataOption(label="Madagascar", value="MG"),
                MetadataOption(label="Maldives", value="MV"),
                MetadataOption(label="Mexico", value="MX"),
                MetadataOption(label="Marshall Islands", value="MH"),
                MetadataOption(label="North Macedonia", value="MK"),
                MetadataOption(label="Mali", value="ML"),
                MetadataOption(label="Malta", value="MT"),
                MetadataOption(label="Myanmar", value="MM"),
                MetadataOption(label="Montenegro", value="ME"),
                MetadataOption(label="Mongolia", value="MN"),
                MetadataOption(label="Northern Mariana Islands", value="MP"),
                MetadataOption(label="Mozambique", value="MZ"),
                MetadataOption(label="Mauritania", value="MR"),
                MetadataOption(label="Montserrat", value="MS"),
                MetadataOption(label="Martinique", value="MQ"),
                MetadataOption(label="Mauritius", value="MU"),
                MetadataOption(label="Malawi", value="MW"),
                MetadataOption(label="Malaysia", value="MY"),
                MetadataOption(label="Mayotte", value="YT"),
                MetadataOption(label="Namibia", value="NA"),
                MetadataOption(label="New Caledonia", value="NC"),
                MetadataOption(label="Niger", value="NE"),
                MetadataOption(label="Norfolk Island", value="NF"),
                MetadataOption(label="Nigeria", value="NG"),
                MetadataOption(label="Nicaragua", value="NI"),
                MetadataOption(label="Niue", value="NU"),
                MetadataOption(label="Netherlands", value="NL"),
                MetadataOption(label="Norway", value="NO"),
                MetadataOption(label="Nepal", value="NP"),
                MetadataOption(label="Nauru", value="NR"),
                MetadataOption(label="New Zealand", value="NZ"),
                MetadataOption(label="Oman", value="OM"),
                MetadataOption(label="Pakistan", value="PK"),
                MetadataOption(label="Panama", value="PA"),
                MetadataOption(label="Pitcairn", value="PN"),
                MetadataOption(label="Peru", value="PE"),
                MetadataOption(label="Philippines", value="PH"),
                MetadataOption(label="Palau", value="PW"),
                MetadataOption(label="Papua New Guinea", value="PG"),
                MetadataOption(label="Poland", value="PL"),
                MetadataOption(label="Puerto Rico", value="PR"),
                MetadataOption(label="Korea, Democratic People's Republic of", value="KP"),
                MetadataOption(label="Portugal", value="PT"),
                MetadataOption(label="Paraguay", value="PY"),
                MetadataOption(label="Palestine, State of", value="PS"),
                MetadataOption(label="French Polynesia", value="PF"),
                MetadataOption(label="Qatar", value="QA"),
                MetadataOption(label="Réunion", value="RE"),
                MetadataOption(label="Romania", value="RO"),
                MetadataOption(label="Russian Federation", value="RU"),
                MetadataOption(label="Rwanda", value="RW"),
                MetadataOption(label="Saudi Arabia", value="SA"),
                MetadataOption(label="Sudan", value="SD"),
                MetadataOption(label="Senegal", value="SN"),
                MetadataOption(label="Singapore", value="SG"),
                MetadataOption(label="South Georgia and the South Sandwich Islands", value="GS"),
                MetadataOption(label="Saint Helena, Ascension and Tristan da Cunha", value="SH"),
                MetadataOption(label="Svalbard and Jan Mayen", value="SJ"),
                MetadataOption(label="Solomon Islands", value="SB"),
                MetadataOption(label="Sierra Leone", value="SL"),
                MetadataOption(label="El Salvador", value="SV"),
                MetadataOption(label="San Marino", value="SM"),
                MetadataOption(label="Somalia", value="SO"),
                MetadataOption(label="Saint Pierre and Miquelon", value="PM"),
                MetadataOption(label="Serbia", value="RS"),
                MetadataOption(label="South Sudan", value="SS"),
                MetadataOption(label="Sao Tome and Principe", value="ST"),
                MetadataOption(label="Suriname", value="SR"),
                MetadataOption(label="Slovakia", value="SK"),
                MetadataOption(label="Slovenia", value="SI"),
                MetadataOption(label="Sweden", value="SE"),
                MetadataOption(label="Eswatini", value="SZ"),
                MetadataOption(label="Sint Maarten (Dutch part)", value="SX"),
                MetadataOption(label="Seychelles", value="SC"),
                MetadataOption(label="Syrian Arab Republic", value="SY"),
                MetadataOption(label="Turks and Caicos Islands", value="TC"),
                MetadataOption(label="Chad", value="TD"),
                MetadataOption(label="Togo", value="TG"),
                MetadataOption(label="Thailand", value="TH"),
                MetadataOption(label="Tajikistan", value="TJ"),
                MetadataOption(label="Tokelau", value="TK"),
                MetadataOption(label="Turkmenistan", value="TM"),
                MetadataOption(label="Timor-Leste", value="TL"),
                MetadataOption(label="Tonga", value="TO"),
                MetadataOption(label="Trinidad and Tobago", value="TT"),
                MetadataOption(label="Tunisia", value="TN"),
                MetadataOption(label="Turkey", value="TR"),
                MetadataOption(label="Tuvalu", value="TV"),
                MetadataOption(label="Taiwan, Province of China", value="TW"),
                MetadataOption(label="Tanzania, United Republic of", value="TZ"),
                MetadataOption(label="Uganda", value="UG"),
                MetadataOption(label="Ukraine", value="UA"),
                MetadataOption(label="United States Minor Outlying Islands", value="UM"),
                MetadataOption(label="Uruguay", value="UY"),
                MetadataOption(label="United States", value="US"),
                MetadataOption(label="Uzbekistan", value="UZ"),
                MetadataOption(label="Holy See (Vatican City State)", value="VA"),
                MetadataOption(label="Saint Vincent and the Grenadines", value="VC"),
                MetadataOption(label="Venezuela, Bolivarian Republic of", value="VE"),
                MetadataOption(label="Virgin Islands, British", value="VG"),
                MetadataOption(label="Virgin Islands, U.S.", value="VI"),
                MetadataOption(label="Viet Nam", value="VN"),
                MetadataOption(label="Vanuatu", value="VU"),
                MetadataOption(label="Wallis and Futuna", value="WF"),
                MetadataOption(label="Samoa", value="WS"),
                MetadataOption(label="Yemen", value="YE"),
                MetadataOption(label="South Africa", value="ZA"),
                MetadataOption(label="Zambia", value="ZM"),
                MetadataOption(label="Zimbabwe", value="ZW"),
            ]
        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        logs_collector = LogsCollector()
        models = model_store.get_models()

        country_group_extractor = models.country_group_extractor
        international_extractor = models.international_extractor
        international_extractor_nb = models.international_extractor_nb
        country_ensemble_extractor = models.country_ensemble_extractor

        docs = document.tokenised_pages

        logs_collector.add("Searching for the countries of investigation...")

        start_time_rule_based = time.time()
        country_to_pages = country_extractor_rule_based.process(docs)
        if len(country_to_pages["prediction"]) > 1:
            country_ies = "countries"
        else:
            country_ies = "country"
        if len(country_to_pages["prediction"]) == 0:
            logs_collector.add("No country was found by rule based country extractor.")
        else:
            logs_collector.add(
                f"From rule based country extractor: It looks like the trial takes place in {len(country_to_pages['prediction'])} {country_ies}: {','.join(country_to_pages['prediction'])}"
            )
        end_time_rule_based = time.time()

        start_time_country_group = time.time()
        country_group_to_pages = country_group_extractor.process(docs)
        end_time_country_group = time.time()

        logs_collector.add(
            f"Neural network found that trial country is likely to be {country_group_to_pages['prediction']}.")

        start_time_int = time.time()
        is_international_to_pages = international_extractor.process(docs)
        end_time_int = time.time()

        logs_collector.add(
            f"Neural network for is trial international? output: {is_international_to_pages['prediction']}.")

        start_time_nb = time.time()
        is_international_nb_to_pages = international_extractor_nb.process(docs)
        end_time_nb = time.time()

        logs_collector.add(
            f"Naive Bayes model for is trial international? output: {is_international_nb_to_pages['prediction']}.")

        start_time_ensemble = time.time()
        ensemble_to_pages = country_ensemble_extractor.process(
            country_to_pages["features"], country_group_to_pages["probas"], is_international_to_pages["probas"],
            is_international_nb_to_pages["score"]
        )
        end_time_ensemble = time.time()

        logs_collector.add(f"Ensemble model output: {json.dumps(ensemble_to_pages)}")

        # is_lmic = len(LMIC_COUNTRIES.intersection(ensemble_to_pages["prediction"])) > 0

        country_to_pages["prediction"] = ensemble_to_pages["prediction"]

        logs_collector.add(
            f"Time to run rule based country classifier: {end_time_rule_based - start_time_rule_based:.4f}")
        logs_collector.add(
            f"Time to run country group classifier: {end_time_country_group - start_time_country_group:.4f}")
        logs_collector.add(f"Time to run int classifier: {end_time_int - start_time_int:.4f}")
        logs_collector.add(f"Time to run nb classifier: {end_time_nb - start_time_nb:.4f}")
        logs_collector.add(f"Time to run ensemble classifier: {end_time_ensemble - start_time_ensemble:.4f}")

        country_to_pages["logs"] = logs_collector.get()

        return country_to_pages


if __name__ == "__main__":
    d = Country()
    document = Document(pages=[Page(content="this is a phase i ii trial in the UK", page_number=1)])
    d_result = d.process(document=document)

    print(json.dumps(d_result, indent=4))

#
# if __name__ == "__main__":
#     d = Country()
#     import pickle as pkl
#     import time
#
#     with open("/home/thomas/clinical_trials/data/ctgov/preprocessed_tika/98_NCT04030598_Prot_SAP_002.pdf.pkl", "rb") as f:
#         pages = pkl.load(f)
#
#     document = Document(
#         pages=[Page(content=p,
#                     page_number=idx+1) for idx, p in enumerate(pages)])
#
#     print ("Number of pages:", len(pages))
#
#     # warm up
#     d_result = d.process(document=document)
#
#     start_time = time.time()
#     print ("started")
#     for i in range(100):
#         d_result = d.process(document=document)
#     end_time = time.time()
#     print(json.dumps(d_result, indent=4))
#
#     print (f"Time elapsed: {end_time-start_time:.5f}")
