import base64
import random
import uuid
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlparse, urlunparse

import pycountry
from sqlalchemy.orm import InstanceState
from sqlmodel import SQLModel

from app.config import CDN_BUCKET_OR_CONTAINER_BASE_PATH
from app.models.user.base import User
from app.types import TSTORAGE_PROVIDER

T = TypeVar("T")


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of specified length."""
    # * Generate a random integer between 10^(length-1) and (10^length) - 1
    return str(random.randint(10 ** (length - 1), (10 ** length) - 1))


def mask_email(email, num_chars_to_keep_username=3, num_chars_to_keep_domain_end=3):
    if "@" in email:
        parts = email.split("@")
        username = parts[0]
        domain = parts[1]

        if len(username) <= num_chars_to_keep_username:
            masked_username = "*" * len(username)
        else:
            masked_username = username[:num_chars_to_keep_username] + "*" * (len(username) - num_chars_to_keep_username)

        if len(domain) <= num_chars_to_keep_domain_end:
            masked_domain = "*" * len(domain)
        else:
            masked_domain = domain[:-num_chars_to_keep_domain_end] + "*" * num_chars_to_keep_domain_end

        return masked_username + "@" + masked_domain
    return email


def serialize_sqlmodel(instance: SQLModel):
    serialized_data = {}

    for attr, value in instance.__dict__.items():
        if isinstance(value, InstanceState):
            continue
        elif isinstance(value, SQLModel):
            serialized_data[attr] = serialize_sqlmodel(value)
        elif isinstance(value, list) and all(isinstance(item, SQLModel) for item in value):
            serialized_data[attr] = [serialize_sqlmodel(item) for item in value]
        else:
            serialized_data[attr] = value

    return serialized_data


def merge_dicts(base: dict, update: dict, readonly_fields: list = []) -> dict:
    """
    Merges two dictionaries. The 'update' dictionary will update values of the 'base' dictionary.
    Fields specified in readonly_fields will not be updated.
    """
    merged = base.copy()
    for key, value in update.items():
        if key not in readonly_fields:
            merged[key] = value
    return merged


def update_instance_from_dict(instance: SQLModel, update_data: dict, readonly_fields: list = []):
    """
    Updates an instance's attributes from a dictionary.
    Only updates attributes that exist on the instance and are in the dictionary.
    Fields specified in readonly_fields will not be updated.
    """
    for key, value in update_data.items():
        if hasattr(instance, key) and value is not None and key not in readonly_fields:
            setattr(instance, key, value)
    return instance


def get_file_extension(url: str) -> str:
    """
    Extracts the file extension from a URL using pathlib.

    Parameters:
        url (str): The URL string.

    Returns:
        str: The file extension without the dot, in lowercase.
             Returns an empty string if no extension is found.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    p = Path(path)
    return p.suffix.lstrip(".").lower()


def remove_file_extension(url: str) -> str:
    """
    Removes the file extension from a URL's path using pathlib.

    Parameters:
        url (str): The URL string.

    Returns:
        str: The URL without the file extension in the path.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    p = Path(path)
    if p.suffix:
        new_path = str(p.with_suffix(""))
    else:
        new_path = path

    # * Reconstruct the URL without the extension
    return urlunparse(parsed_url._replace(path=new_path))


def img_to_base64(image_bytes: bytes) -> str:
    """
    Image to base64.

    :param image_bytes: The image in bytes.
    :returns: The image base64 encoded.
    """

    return base64.b64encode(image_bytes).decode("utf-8")


def yes_or_no(x: Any) -> str:
    """
    Return "yes" if value is truthy, else return False.
    """

    if x:
        return "Yes"

    return "No"


def pretty_print_countries(countries: list[str], show_flags: bool = False) -> str:
    """
    Output the list of countries found in the document in a human-readable phone optionally showing flags as Unicode
    characters, which may not be displayed on all platforms

    :param countries: The list of countries as 2-letter country codes, which will be used to retrieve PyCountry objects.
    :param show_flags: whether flags of the country should be displayed or not.
    :return: A human-readable string separated by commas which can be used for natural language generation (NLG).
    """

    if len(countries) == 0:
        return "No countries of sufficient confidence."

    human_readable_prediction = ""
    for idx, country_code in enumerate(countries):
        if idx > 0:
            human_readable_prediction += ","
        human_readable_prediction += " "
        if country_code == "XX":
            human_readable_prediction += "one or more unspecified countries"
        else:
            if show_flags:
                human_readable_prediction += pycountry.countries.get(
                    alpha_2=country_code
                ).flag
            human_readable_prediction += pycountry.countries.get(alpha_2=country_code).name

    return human_readable_prediction


def create_analysis_report_file_storage_key(
    user_resource_identifier: str,
    filename: str,
    storage_provider: TSTORAGE_PROVIDER
) -> str:
    """
    Create analysis report file storage key.

    :param user_resource_identifier: The user resource identifier.
    :param filename: The filename.
    :param storage_provider: The storage provider.
    """

    if not is_valid_uuid(user_resource_identifier):
        raise Exception(f"Invalid user_resource_identifier received: {user_resource_identifier}.")

    filename = filename.strip()
    if not is_valid_filename(filename):
        raise Exception(f"Invalid filename received: {filename}.")

    analysis_report_data = "analysis-report-data"
    if storage_provider == "local":
        return f"{analysis_report_data}/{user_resource_identifier}/{filename}"
    else:
        return f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/{analysis_report_data}/{user_resource_identifier}/{filename}"


def create_document_file_storage_key(
    user_resource_identifier: str,
    filename: str,
    storage_provider: TSTORAGE_PROVIDER
) -> str:
    """
    Create document file storage key.

    :param user_resource_identifier: The user resource identifier.
    :param filename: The filename.
    :param storage_provider: The storage provider.
    """

    if not is_valid_uuid(user_resource_identifier):
        raise Exception(f"Invalid user_resource_identifier received: {user_resource_identifier}.")

    filename = filename.strip()
    if not is_valid_filename(filename):
        raise Exception(f"Invalid filename received: {filename}.")

    documents = "documents"
    if storage_provider == "local":
        return f"{documents}/{user_resource_identifier}/{filename}"
    else:
        return f"{CDN_BUCKET_OR_CONTAINER_BASE_PATH}/{documents}/{user_resource_identifier}/{filename}"


def split_list_into_chunks(l: list[T], n: int) -> list[list[T]]:
    """
    Split list into chunks.

    :param l: The list to split.
    :param n: Size per chunk.
    """

    return [l[i:i + n] for i in range(0, len(l), n)]


def is_valid_uuid(value: str) -> bool:
    """
    Check if UUID is valid.

    :param value: The value to check.
    """

    try:
        uuid.UUID(value)

        return True
    except ValueError:
        return False


def is_valid_filename(value: str) -> bool:
    """
    Check if filename is valid.

    :param value: The value to check.
    """

    if not value or value.endswith("."):
        return False

    forbidden_characters: set[str] = {"/", "\\"}
    for char in value:
        if char in forbidden_characters:
            return False

    return True
