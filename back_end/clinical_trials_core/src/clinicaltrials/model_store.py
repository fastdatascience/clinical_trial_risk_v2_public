import bz2
import logging
import threading
from dataclasses import dataclass
from pickle import load as pickle_load
from typing import Any, cast

from clinicaltrials.core import __get_logger
from clinicaltrials.country.country_ensemble_extractor import CountryEnsembleExtractor
from clinicaltrials.country.country_group_extractor import CountryGroupExtractor
from clinicaltrials.country.international_extractor_naive_bayes import InternationalExtractorNaiveBayes
from clinicaltrials.country.international_extractor_spacy import InternationalExtractorSpacy

country_group_extractor = None
international_extractor = None
international_extractor_nb = None
country_ensemble_extractor = None
age_model: Any | None = None

_model_load_lock = threading.Lock()
logger = __get_logger(log_level=logging.DEBUG)


@dataclass(frozen=True)
class ClinicalModel:
    """
    Dataclass representing clinical trial models with lazy loading
    """

    country_group_extractor: CountryGroupExtractor
    international_extractor: InternationalExtractorSpacy
    international_extractor_nb: InternationalExtractorNaiveBayes
    country_ensemble_extractor: CountryEnsembleExtractor
    age_model: Any


def initialize_models(path_to_classifier: str) -> None:
    """
    Loads the models if they are not already loaded
    This function is idempotent: calling it multiple times
    will load the models only once.
    """
    logger.info(f"Initializing models from disk @ {path_to_classifier}...")

    global country_group_extractor, international_extractor, international_extractor_nb, country_ensemble_extractor, age_model

    if all(m is not None for m in [country_group_extractor, international_extractor, international_extractor_nb, country_ensemble_extractor, age_model]):
        return

    with _model_load_lock:
        if all(m is not None for m in [country_group_extractor, international_extractor, international_extractor_nb, country_ensemble_extractor, age_model]):
            return

        logger.info(f"Initializing models from {path_to_classifier}")

        country_group_extractor = CountryGroupExtractor(f"{path_to_classifier}/spacy-textcat-country-16-model-best")
        international_extractor = InternationalExtractorSpacy(f"{path_to_classifier}/spacy-textcat-international-11-model-best")
        international_extractor_nb = InternationalExtractorNaiveBayes(f"{path_to_classifier}/international_classifier.pkl.bz2")
        country_ensemble_extractor = CountryEnsembleExtractor(f"{path_to_classifier}/country_ensemble_model.pkl.bz2")

        with bz2.open(f"{path_to_classifier}/age_classifier.pkl.bz2", "rb") as f:
            age_model = pickle_load(f)

        logger.info("All models initialized successfully")


def get_models() -> ClinicalModel:
    """
    Returns initialized models as a dataclass instance
    Uses cast with string type references to avoid imports
    """
    if any(m is None for m in [country_group_extractor, international_extractor, international_extractor_nb, country_ensemble_extractor, age_model]):
        raise ValueError("Models not initialized. Call initialize_models() first.")

    return ClinicalModel(
        country_group_extractor=cast(CountryGroupExtractor, country_group_extractor),
        international_extractor=cast(InternationalExtractorSpacy, international_extractor),
        international_extractor_nb=cast(InternationalExtractorNaiveBayes, international_extractor_nb),
        country_ensemble_extractor=cast(CountryEnsembleExtractor, country_ensemble_extractor),
        age_model=age_model,
    )
