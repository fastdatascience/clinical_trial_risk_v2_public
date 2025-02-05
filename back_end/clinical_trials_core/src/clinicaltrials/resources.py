import spacy

nlp = spacy.blank("en")

# todo change the key to have nested model definitions
CLASSIFIER_BIN = {
    "phase": "https://fastdatascience.z33.web.core.windows.net/clinical/phase.zip",
    "condition": "https://fastdatascience.z33.web.core.windows.net/clinical/condition_classifier_small.pkl.bz2",
    "vaccine": "https://fastdatascience.z33.web.core.windows.net/clinical/vaccine_classifier.pkl.bz2",
    "intervention_type": "https://fastdatascience.z33.web.core.windows.net/clinical/intervention_classifier.pkl.bz2",
    "country": "https://fastdatascience.z33.web.core.windows.net/clinical/country.zip",
    "effect_estimate": "https://fastdatascience.z33.web.core.windows.net/clinical/effect_estimate_classifier.pkl.bz2",
    "simulation": "https://fastdatascience.z33.web.core.windows.net/clinical/simulation_classifier.pkl.bz2",
    "sample_size": "https://fastdatascience.z33.web.core.windows.net/clinical/num_subjects_classifier.pkl.bz2",
    "sap": "https://fastdatascience.z33.web.core.windows.net/clinical/sap.zip",
    "num_arms": "https://fastdatascience.z33.web.core.windows.net/clinical/arms.zip",
    "healthy": "https://fastdatascience.z33.web.core.windows.net/clinical/healthy_classifier.pkl.bz2",
    "gender": "https://fastdatascience.z33.web.core.windows.net/clinical/gender_classifier.pkl.bz2",
    "age": "https://fastdatascience.z33.web.core.windows.net/clinical/age_classifier.pkl.bz2",
    "child": "https://fastdatascience.z33.web.core.windows.net/clinical/child_classifier.pkl.bz2",
    "placebo": "https://fastdatascience.z33.web.core.windows.net/clinical/placebo_classifier.pkl.bz2",
    "drug": "https://fastdatascience.z33.web.core.windows.net/clinical/drug_classifier.pkl.bz2",
    "duration": "https://fastdatascience.z33.web.core.windows.net/clinical/duration_nb_classifier.pkl.bz2",
    "idfs_wordcloud": "https://fastdatascience.z33.web.core.windows.net/clinical/idfs_for_word_cloud.pkl.bz2",
}
