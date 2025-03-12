"""
Fixtures should be imported to conftest.py of the test package when needed e.g. to
tests/transform_tests/conftest.py.
"""

import json
import os.path
from typing import Generator, Any

import pytest
import requests

from clinicaltrials import model_store
from clinicaltrials.core import CoreUtil, ClinicalTrial, Metadata
from clinicaltrials.schemas import WeightProfileBase


@pytest.fixture(scope="session", autouse=True)
def sync_and_initialize_models() -> Generator[None, Any, None]:
    """
    Sync and initialize models.
    """

    # Setup
    CoreUtil.sync_classifier_models()
    model_store.initialize_models("/tmp")

    yield

    # Teardown


@pytest.fixture(scope="session", autouse=True)
def weight_profile_base() -> Generator[WeightProfileBase, Any, None]:
    """
    Get weight profile.

    The weight profile and tests should be updated when:
     * The data structure of the weight profile has changed.
     * New data was added that requires new tests e.g. new cost/risk model.
    """

    # Setup
    filepath = "tests/fixtures/weight_schema_v2.json"
    if not os.path.isfile(filepath):
        response = requests.get(
            url="https://clinicaltrialsv2storage.z33.web.core.windows.net/assets/test_data/weight_schema_v2.json"
        )
        if response.ok:
            with open(filepath, "wb") as file:
                file.write(response.content)
        else:
            response.raise_for_status()

    with open(filepath, "r") as file:
        weight_profile_dict: dict = json.loads(file.read())

    yield WeightProfileBase(**weight_profile_dict)

    # Teardown


@pytest.fixture(scope="session", autouse=True)
def user_resource_usage() -> Generator[dict, Any, None]:
    """
    Get user resource usage.
    """

    # Setup
    filepath = "tests/fixtures/user_resource_usage.json"
    if not os.path.isfile(filepath):
        response = requests.get(
            url="https://clinicaltrialsv2storage.z33.web.core.windows.net/assets/test_data/user_resource_usage.json"
        )
        if response.ok:
            with open(filepath, "wb") as file:
                file.write(response.content)
        else:
            response.raise_for_status()

    with open(filepath, "r") as file:
        user_resource_usage_dict: dict = json.loads(file.read())

    yield user_resource_usage_dict

    # Teardown


@pytest.fixture(scope="session", autouse=True)
def metadata() -> Generator[list[Metadata], Any, None]:
    """
    Get metadata.
    """

    # Setup
    metadata = ClinicalTrial().metadata

    yield metadata

    # Teardown
