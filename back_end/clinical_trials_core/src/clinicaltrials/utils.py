import os

from clinicaltrials.schemas import Tertile


def get_default_classifier_storage_path() -> str:
    return "/tmp" if os.name == "posix" else "C:\\temp"


def find_matching_tertile_by_priority(priority: list[tuple], tertiles: list[Tertile]) -> Tertile | None:
    """
    Find the first matching tertile based on priority.
    """

    for condition, phase in priority:
        matching_tertile = next(
            (tertile for tertile in tertiles if tertile.condition == condition and tertile.phase == phase),
            None
        )
        if matching_tertile:
            return matching_tertile


def list_has_1_item_or_more(value: list | set) -> int:
    """
    If the list has 1 item or more, return 1, else return 0.
    """

    if type(value) is list or type(value) is set:
        return int(len(value) > 0)

    return 0


def list_has_2_items_or_more(value: list | set) -> int:
    """
    If the list has 2 items or more, return 1, else return 0.
    """

    if type(value) is list or type(value) is set:
        return int(len(value) > 1)

    return 0
