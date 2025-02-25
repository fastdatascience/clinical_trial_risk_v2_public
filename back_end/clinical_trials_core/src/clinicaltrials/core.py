"""
core.py

This module provides core functions and objects for running an analysis on clinical trial documents.

Usage:
    from clinicaltrials.core import ClinicalTrial
    ct = ClinicalTrial()
    result = ct.run_all(document=parsed_document, parallel=True, file_buffer=file_contents)
"""

__version__ = "1.2.1"

import argparse
import inspect
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from io import BytesIO
from os import path
from threading import Thread
from typing import Any, Callable, Literal, Self, TypeAlias
from zipfile import ZipFile

import requests
from pdfplumber import open as pdfplumber_open
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from spacy.tokens import Doc

from clinicaltrials.resources import CLASSIFIER_BIN
from clinicaltrials.resources import nlp as spacy_nlp
from clinicaltrials.utils import get_default_classifier_storage_path


def __get_logger(log_level=logging.DEBUG, log_to_file=False, log_file="logfile.log"):
    logger = logging.getLogger()
    logger.setLevel(level=log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(fmt=formatter)

    logger.addHandler(console_handler)

    if log_to_file:
        try:
            file_handler = logging.FileHandler(filename=log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(fmt=formatter)
            logger.addHandler(hdlr=file_handler)
        except Exception as e:
            logger.warning(f"Failed to create log file: {e}")

    return logger


Table: TypeAlias = list[list[str | None]]
Tables: TypeAlias = list[list[list[str | None]]]


@dataclass
class PageAnnotation:
    text: str
    type: str
    page_no: int
    subtype: str
    end_char: int
    start_char: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "PageAnnotation":
        return PageAnnotation(
            text=data.get("text", ""),
            type=data.get("type", ""),
            page_no=data.get("page_no", 0),
            subtype=data.get("subtype", ""),
            end_char=data.get("end_char", 0),
            start_char=data.get("start_char", 0),
        )


class PageMarker:
    __words_to_highlight: list[str] = []

    def add_highlight(self, word: str):
        self.__words_to_highlight.append(word)

    def delete_highlight(self, word: str):
        self.__words_to_highlight.remove(word)

    @property
    def markers(self):
        return self.__words_to_highlight


@dataclass
class Page:
    page_number: int
    content: str

    """
    List of 2d Matrices
    table -> row -> cell
    """
    tables: list[Table] = field(default_factory=lambda: [])

    marker: PageMarker = PageMarker()


class Document:
    """
    Class representing document object for clinical trails. Created after parsing the document
    """

    pages: list[Page]
    metadata: dict | None = None

    def __init__(self, pages: list[Page], metadata: dict | None = None, file_buffer: bytes | None = None):
        self.logger = logging.getLogger()
        self.logger.name = __class__.__name__

        self.pages = pages
        self.metadata = metadata

        if file_buffer:
            self.extract_tables(file_buffer=file_buffer)

    @staticmethod
    def pdf_to_document(pdf_path: str) -> "Document":
        abs_pdf_path = path.abspath(pdf_path)
        pages = []
        metadata: dict | None = None

        with pdfplumber_open(path_or_fp=abs_pdf_path) as pdf_buffer:
            for page_number in range(len(pdf_buffer.pages)):
                page = pdf_buffer.pages[page_number]

                content = page.extract_text()

                table = page.extract_tables()

                pages.append(Page(page_number=page_number + 1, content=content, tables=table))

            metadata = pdf_buffer.metadata

        return Document(pages, metadata=metadata)

    @property
    def tokenised_pages(self) -> list[Doc]:
        """
        Process the raw text of each page in the document with spaCy and return a list of spaCy Doc objects. Ideally we only do this once.
        We replace all newlines and multiple spaces with single spaces, because otherwise spaCy makes them into a new token which interferes with matching.

        Returns: List of Docs, where each Doc corresponds to a page
        """

        return list(spacy_nlp.pipe([re.sub(r"\s+", " ", page.content) for page in self.pages]))

    def extract_tables(self, file_buffer: bytes) -> None:
        with pdfplumber_open(path_or_fp=BytesIO(file_buffer)) as pdf_buffer:
            if len(pdf_buffer.pages) != len(self.pages):
                self.logger.warning("Mismatch between file buffer and pages provided")
                return

            for page_number in range(len(pdf_buffer.pages)):
                self.logger.debug(f"Extracting table from page {page_number}")
                page = pdf_buffer.pages[page_number]
                table = page.extract_tables()

                self.pages[page_number].tables = table


@dataclass
class ClassifierConfig:
    path_to_classifier: str = ""
    # * Provide custom path to persist models. Defaults to volatile storage path
    classifier_storage_path: str = get_default_classifier_storage_path()


class ClassifierConfigException(Exception):
    def __init__(self, message: str = "Missing Classifier configuration") -> None:
        super().__init__(message)


@dataclass
class MetadataOption:
    label: str
    value: str | int


@dataclass
class Metadata:
    id: str
    name: str
    feature_type: Literal["yesno", "categorical", "numeric", "multi_label", "key_value_list", "numeric_range"]
    options: list[MetadataOption] | list[dict[str, str]] = field(default_factory=list)
    default_weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        # * Ensure "cost" and "risk" are in default_weights with default values if not provided
        self.default_weights.setdefault("cost", 0.0)
        self.default_weights.setdefault("risk", 0.0)

        self.validate()

    def to_dict(self) -> dict:
        return asdict(self)

    def get_description(self, selected_value):
        if self.feature_type in ["numeric", "yesno"] or self.id == "phase":
            return self.name
        if self.feature_type == "multi_label":
            if isinstance(selected_value, list) and selected_value:
                return ", ".join(str(value) for value in selected_value)
            return "_"
        if isinstance(selected_value, list):
            return ", ".join(str(value) for value in selected_value)
        return str(selected_value) if selected_value is not None else "_"

    def get_value(self, selected_value, prediction):
        if self.id != "phase" and self.feature_type in ["categorical", "multi_label", "numeric_range"]:
            if selected_value or isinstance(selected_value, list):
                return 1
            return 0
        if self.feature_type == "yesno":
            if selected_value in ["yes", "no"]:
                return 1 if selected_value == "yes" else 0

        if selected_value:
            return selected_value
        return prediction

    def validate(self):
        """
        Validate the options based on the feature_type.

        Raises:
            ValueError: If feature_type is 'key_value_list' and any option is not a dictionary.
            ValueError: If feature_type is not 'key_value_list' and any option is not an instance of MetadataOption.

        Examples:
            >>> # Valid example for feature_type 'key_value_list'
            >>> metadata = Metadata(
            >>>     id="123",
            >>>     name="Example Metadata",
            >>>     feature_type="key_value_list",
            >>>     options=[{"key1": "value1"}, {"key2": "value2"}]
            >>> )
            >>> metadata.validate()  # Should pass without error

            >>> # Invalid example for feature_type 'key_value_list'
            >>> metadata = Metadata(
            >>>     id="123",
            >>>     name="Example Metadata",
            >>>     feature_type="key_value_list",
            >>>     options=[MetadataOption(label="Option1", value="Value1")]
            >>> )
            >>> metadata.validate()  # Should raise ValueError

            >>> # Valid example for feature_type 'categorical'
            >>> metadata = Metadata(
            >>>     id="123",
            >>>     name="Example Metadata",
            >>>     feature_type="categorical",
            >>>     options=[MetadataOption(label="Option1", value="Value1")]
            >>> )
            >>> metadata.validate()  # Should pass without error

            >>> # Invalid example for feature_type 'categorical'
            >>> metadata = Metadata(
            >>>     id="123",
            >>>     name="Example Metadata",
            >>>     feature_type="categorical",
            >>>     options=[{"key1": "value1"}, {"key2": "value2"}]
            >>> )
            >>> metadata.validate()  # Should raise ValueError
        """
        if self.feature_type == "key_value_list":
            if not all(isinstance(option, dict) for option in self.options):
                raise ValueError("All options must be dictionaries for key_value_list feature type")
        else:
            if not all(isinstance(option, MetadataOption) for option in self.options):
                raise ValueError(f"All options must be MetadataOption instances for {self.feature_type} feature type")


class BaseProcessor(ABC):
    """Base class for all processors."""

    def __init__(self, module_name: str = "base_processor") -> None:
        super().__init__()

        self.logger = logging.getLogger()
        self.logger.name = __class__.__name__

        # * Points to the classname of child classes
        self.__module_name = module_name

        self.config: ClassifierConfig | None = None

    @abstractmethod
    def process(self, document: Document, config: ClassifierConfig | None = None):
        raise NotImplementedError("Subclasses must implement the 'process' method.")

    @property
    @abstractmethod
    def metadata(self) -> Metadata | None:
        """Optional metadata property to be defined in child classes."""
        return None

    def set_config(self, config: ClassifierConfig) -> Self:
        self.config = config
        return self

    @property
    def module_name(self) -> str:
        return "".join(["_" + char.lower() if char.isupper() else char for char in self.__module_name]).lstrip("_")

    def get_classifier_config_or_default(self, config: ClassifierConfig | None) -> ClassifierConfig:
        if config and config.path_to_classifier:
            return config

        key = self.module_name
        self.logger.info(f"Get classifier config for module {key}")

        if key not in CLASSIFIER_BIN:
            self.logger.error(f"Invalid module {key}")
            raise ClassifierConfigException()

        remote_file_path = CLASSIFIER_BIN[key]

        file_name = remote_file_path.split("/")[-1]

        # * Just to make sure, should not hit edge case but its here for good measures
        if self.config is None:
            self.logger.info("Config is None, creating new default config")
            self.config = ClassifierConfig(path_to_classifier="")

        if not path.exists(path=f"{self.config.classifier_storage_path.rstrip('/')}/{file_name}"):
            CoreUtil.sync_classifier_models(config=self.config, key=key)

        # * Set the full path in case of direct classifier else set the directory that contains multiple classifiers
        self.config.path_to_classifier = (
            f"{self.config.classifier_storage_path.rstrip('/')}/{file_name}" if not file_name.endswith(".zip") else self.config.classifier_storage_path.rstrip("/")
        )

        return self.config


@dataclass
class EventData:
    data: Any
    type: Literal["completion_progress", "message"]

    def __post_init__(self):
        if self.type not in ("completion_progress", "message"):
            raise ValueError("Invalid type. Allowed values are 'completion_progress' or 'message'.")


class Event:
    def __init__(self):
        self._subscribers: list[Callable[..., Any]] = []

    def subscribe_raw(self, callback: Callable[..., Any]) -> None:
        self._subscribers.append(callback)

    def subscribe(self, callback: Callable[[EventData], None]) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[..., Any]) -> None:
        self._subscribers.remove(callback)

    def notify_raw(self, *args: Any, **kwargs: Any) -> None:
        for subscriber in self._subscribers:
            subscriber(*args, **kwargs)

    def notify(self, event_data: EventData) -> None:
        for subscriber in self._subscribers:
            subscriber(event_data)


class ClinicalTrial:
    from .age import Age
    from .biobank import Biobank
    from .child import Child
    from .cohort_size import CohortSize
    from .condition import Condition
    from .consent import Consent
    from .control_negative import ControlNegative
    from .country import Country
    from .design import Design
    from .document_type import DocumentType
    from .drug import Drug
    from .duration import Duration
    from .effect_estimate import EffectEstimate
    from .gender import Gender
    from .healthy import Healthy
    from .human_challenge import HumanChallenge
    from .interim import Interim
    from .intervention_type import InterventionType
    from .master_protocol import MasterProtocol
    from .num_arms import NumArms
    from .num_interventions_per_visit import NumInterventionsPerVisit
    from .num_interventions_total import NumInterventionsTotal
    from .num_sites import NumSites
    from .num_visits import NumVisits
    from .overnight_stay import OvernightStay
    from .phase import Phase
    from .placebo import Placebo
    from .platform_trial import PlatformTrial
    from .randomisation import Randomisation
    from .regimen import Regimen
    from .regimen_duration import RegimenDuration
    from .sample_size import SampleSize
    from .sap import Sap
    from .simulation import Simulation
    from .vaccine import Vaccine

    __loaded_modules: dict[str, type[BaseProcessor]] = {
        "drug": Drug,
        "phase": Phase,
        "condition": Condition,
        "country": Country,
        "effect_estimate": EffectEstimate,
        "simulation": Simulation,
        "sample_size": SampleSize,
        "sap": Sap,
        "num_arms": NumArms,
        "cohort_size": CohortSize,
        "biobank": Biobank,
        "num_sites": NumSites,
        "duration": Duration,
        "num_visits": NumVisits,
        "num_interventions_per_visit": NumInterventionsPerVisit,
        "num_interventions_total": NumInterventionsTotal,
        "design": Design,
        "consent": Consent,
        "randomisation": Randomisation,
        "control_negative": ControlNegative,
        "healthy": Healthy,
        "gender": Gender,
        "age": Age,
        "child": Child,
        "placebo": Placebo,
        "regimen": Regimen,
        "interim": Interim,
        "document_type": DocumentType,
        "vaccine": Vaccine,
        "intervention_type": InterventionType,
        "overnight_stay": OvernightStay,
        "human_challenge": HumanChallenge,
        "regimen_duration": RegimenDuration,
        "master_protocol": MasterProtocol,
        "platform_trial": PlatformTrial,
    }

    def __init__(self, classifier_config: ClassifierConfig | None = None) -> None:
        """
        Initialize ClinicalTrial object.

        Parameters:
        - config: An optional instance of :class:`ClinicalTrialConfig` containing configuration options.
                  If not provided, default configuration options will be used.
        """
        self.logger = logging.getLogger()
        self.logger.name = __class__.__name__

        self.__run_completed_modules = 0
        self.event = Event()

        if classifier_config is None:
            classifier_config = ClassifierConfig()

        self.classifier_config = classifier_config

        self.__check_modules()

    def __check_modules(self):
        """
        Checks if all classes in 'modules' extend from BaseProcessor.
        Raises RuntimeError if any class does not.
        """
        for module in self.__loaded_modules.values():
            direct_inheritance = module.__base__ is BaseProcessor
            if not direct_inheritance:
                raise RuntimeError(f"{module.__name__} does not extend BaseProcessor")

    @property
    def modules(self):
        """
        Get list of modules loaded
        """
        return list(self.__loaded_modules.keys())

    @property
    def modules_len(self):
        """Number of modules loaded"""
        return len(self.__loaded_modules.keys())

    @property
    def metadata(self) -> list[Metadata]:
        metadata_list: list[Metadata] = []
        for name, processor_cls in self.__loaded_modules.items():
            try:
                processor = processor_cls()
                if processor.metadata is not None:
                    metadata_list.append(processor.metadata)

            except TypeError as e:
                self.logger.debug(f"Could not instantiate {name}: {e}")

        return metadata_list

    @property
    def metadata_dict(self) -> list[dict]:
        metadata_list: list[Metadata] = self.metadata
        metadata_dict = [metadata.to_dict() for metadata in metadata_list]
        return metadata_dict

    def human_readable(self, text: str):
        words = text.split("_")
        capitalized_words = [word.capitalize() for word in words]
        return " ".join(capitalized_words)

    def get_module(self, module_name: str) -> BaseProcessor:
        if module_name not in self.__loaded_modules:
            raise Exception("Invalid module")

        instance = self.__loaded_modules[module_name]()
        instance.set_config(self.classifier_config)

        return instance

    def __run_module(self, module_instance: BaseProcessor, document: Document, config: ClassifierConfig, accumulator_dict: dict[str, Any]):
        start_time = time.time()
        self.logger.info(f"Module {module_instance.module_name} run started")
        self.event.notify(EventData(type="message", data=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Module {self.human_readable(module_instance.module_name)} run started"))

        if "config" in inspect.signature(obj=module_instance.process).parameters:
            result = module_instance.process(document=document, config=config)
        else:
            result = module_instance.process(document=document)

        accumulator_dict[module_instance.module_name] = result

        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.info(f"Module {module_instance.module_name} run complete in {execution_time} seconds")

        # * Notify about the run completion
        self.event.notify(
            EventData(
                type="message",
                data=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Module {self.human_readable(module_instance.module_name)} run complete in {execution_time} seconds",
            )
        )

        # * Increment the run completed modules counter
        self.__run_completed_modules += 1

        # * Calculate progress
        if self.modules_len > 0:
            progress = self.__run_completed_modules / self.modules_len * 100
            self.logger.info(f"Completion: {progress:.2f}%")
            self.event.notify(EventData(type="completion_progress", data=progress))

        return accumulator_dict

    def run_all(
        self, document: Document, config: ClassifierConfig | None = None, parallel: bool = False, exclude_modules: list[str] = [], file_buffer: bytes | None = None
    ) -> dict[str, Any]:
        hot_modules = {key: value for key, value in self.__loaded_modules.items() if key not in exclude_modules}
        self.logger.info(f"Running {len(hot_modules.keys())} modules")

        accumulator_dict: dict[str, Any] = {}
        if parallel:
            threads: list[Thread] = []

            for module in hot_modules.values():
                module_instance = module()
                thread = Thread(target=self.__run_module, args=(module_instance, document, self.classifier_config or config, accumulator_dict))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        else:
            for module in hot_modules.values():
                module_instance = module()
                self.__run_module(module_instance=module_instance, document=document, config=self.classifier_config or config, accumulator_dict=accumulator_dict)

            # * Add highlights to the pdf
            if file_buffer is not None:
                pass

        return accumulator_dict


class CoreUtil:
    __core_util_logger = logging.getLogger()

    @staticmethod
    def find_key_in_nested_dicts(data: dict, target_key: str) -> list[Any]:
        results = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key == target_key:
                    results.append(value)
                else:
                    results.extend(CoreUtil.find_key_in_nested_dicts(value, target_key))
        elif isinstance(data, list):
            for item in data:
                results.extend(CoreUtil.find_key_in_nested_dicts(item, target_key))

        return results

    @staticmethod
    def download_file(url: str, save_path: str) -> bool:
        logging.getLogger().info(f"Downloading {url} to {save_path}")
        with requests.get(url, stream=True) as response:
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    # * Initialize variables to track progress
                    total_size = int(response.headers.get("content-length", 0))
                    bytes_received = 0

                    # * Iterate over the response content in chunks
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                        bytes_received += len(chunk)

                        progress = min(100, int(bytes_received / total_size * 100))
                        print(f"Download progress: {progress}% ({bytes_received}/{total_size} bytes)", end="\r")

                logging.getLogger().info("Download completed successfully")
                return True
            else:
                logging.getLogger().error(f"Failed to download file. Status code: {response.status_code}")
                return False

    @staticmethod
    def sync_classifier_models(config: ClassifierConfig = ClassifierConfig(path_to_classifier=""), key: str | None = None):
        def process_classifier(key: str):
            remote_file_path = CLASSIFIER_BIN[key]

            file_name = remote_file_path.split("/")[-1]
            file_path = f"{config.classifier_storage_path.rstrip('/')}/{file_name}"

            success = CoreUtil.download_file(url=remote_file_path, save_path=file_path)

            if not success:
                logging.getLogger().error("Classifier download failed")
                raise ClassifierConfigException()

            # * Check if file is .zip and extract it
            if file_name.endswith(".zip"):
                logging.getLogger().info("Extracting classifiers")
                with ZipFile(file=file_path, mode="r") as zip_ref:
                    zip_ref.extractall(path=config.classifier_storage_path.rstrip("/"))

        if key:
            if key not in CLASSIFIER_BIN:
                logging.getLogger().error(f"Key '{key}' not found in CLASSIFIER_BIN")
                raise ClassifierConfigException()

            logging.getLogger().info(f"Processing classifier for key: {key}")
            process_classifier(key)
        else:
            for key in CLASSIFIER_BIN.keys():
                logging.getLogger().info(f"Processing classifier for key: {key}")
                process_classifier(key)


if __name__ == "__main__":
    # * Parse the log level argument from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("-log", "--log", help="Provide logging level. Example --log debug'")
    args = parser.parse_args()
    log_level = args.log if args.log else "INFO"

    __get_logger(log_level=getattr(logging, log_level.upper()))
