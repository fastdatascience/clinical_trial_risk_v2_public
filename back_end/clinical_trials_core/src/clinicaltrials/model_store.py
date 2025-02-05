import logging
import threading
from dataclasses import dataclass

from clinicaltrials.core import __get_logger
from clinicaltrials.country.country_ensemble_extractor import CountryEnsembleExtractor
from clinicaltrials.country.country_group_extractor import CountryGroupExtractor
from clinicaltrials.country.international_extractor_naive_bayes import InternationalExtractorNaiveBayes
from clinicaltrials.country.international_extractor_spacy import InternationalExtractorSpacy

country_group_extractor = None
international_extractor = None
international_extractor_nb = None
country_ensemble_extractor = None

_model_load_lock = threading.Lock()

logger = __get_logger(log_level=logging.DEBUG)


@dataclass
class Model:
    pass


def initialize_models(path_to_classifier: str):
    """
    Loads the models if they are not already loaded
    This function is idempotent: calling it multiple times
    will load the models only once.
    """
    logger.info(f"Initializing models from disk @ {path_to_classifier}...")
    global country_group_extractor, international_extractor, international_extractor_nb, country_ensemble_extractor

    # * Check if already loaded
    if country_group_extractor is not None and international_extractor is not None and international_extractor_nb is not None and country_ensemble_extractor is not None:
        return

    with _model_load_lock:
        # * Double check inside lock
        if country_group_extractor is not None and international_extractor is not None and international_extractor_nb is not None and country_ensemble_extractor is not None:
            return

        country_group_extractor = CountryGroupExtractor(f"{path_to_classifier}/spacy-textcat-country-16-model-best")
        international_extractor = InternationalExtractorSpacy(f"{path_to_classifier}/spacy-textcat-international-11-model-best")
        international_extractor_nb = InternationalExtractorNaiveBayes(f"{path_to_classifier}/international_classifier.pkl.bz2")
        country_ensemble_extractor = CountryEnsembleExtractor(f"{path_to_classifier}/country_ensemble_model.pkl.bz2")

    logger.info("Initializing models from disk completed")


def get_models():
    """
    Returns the loaded model instances.
    Make sure to call initialize_models(path_to_classifier) before this.
    """
    if any(m is None for m in [country_group_extractor, international_extractor, international_extractor_nb, country_ensemble_extractor]):
        raise ValueError("Models are not initialized. Call initialize_models(path_to_classifier) first.")

    return {
        "country_group_extractor": country_group_extractor,
        "international_extractor": international_extractor,
        "international_extractor_nb": international_extractor_nb,
        "country_ensemble_extractor": country_ensemble_extractor,
    }
