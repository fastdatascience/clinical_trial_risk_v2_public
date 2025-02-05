from typing import Any, Literal

from clinicaltrials.core import Metadata, MetadataOption


def get_derived_modules_and_metadata() -> tuple[tuple[Literal["lmic"], Literal["international"]], tuple[dict[Any, Any], ...], tuple["Metadata", "Metadata"]]:
    modules = ("lmic", "international")
    metadata = (
        Metadata(id="lmic", name="Low to medium income country", feature_type="yesno", options=[MetadataOption(label="yes", value=1), MetadataOption(label="no", value=0)]),
        Metadata(id="international", name="International", feature_type="yesno", options=[MetadataOption(label="yes", value=1), MetadataOption(label="no", value=0)]),
    )

    metadata_dict = tuple(metadata_item.to_dict() for metadata_item in metadata)

    return modules, metadata_dict, metadata
