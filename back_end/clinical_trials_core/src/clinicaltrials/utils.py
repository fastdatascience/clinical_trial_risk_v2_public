import os


def get_default_classifier_storage_path() -> str:
    return "/tmp" if os.name == "posix" else "C:\\temp"
