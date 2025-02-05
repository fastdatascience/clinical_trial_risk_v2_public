import argparse
import logging
import os
import shutil
import subprocess
from urllib.parse import urlparse

from clinicaltrials.core import ClassifierConfig, CoreUtil
from clinicaltrials.utils import get_default_classifier_storage_path

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

__version__ = "0.1"


def download_protocols(download_path: str):
    urls = [
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT00006400/Prot_SAP_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT00150800/Prot_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT00553800/Prot_SAP_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT00943800/Prot_SAP_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT01030900/Prot_SAP_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT01197300/Prot_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT01212900/Prot_SAP_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT01532700/Prot_SAP_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT01557400/Prot_000.pdf",
        "https://ClinicalTrials.gov/ProvidedDocs/00/NCT01731600/Prot_000.pdf",
    ]

    if not os.path.exists(download_path):
        logger.info(f"Creating directory: {download_path}")
        os.makedirs(download_path, exist_ok=True)

    wget_path = shutil.which(cmd="wget")
    if wget_path is None:
        logger.error("wget not found in system PATH")
        return

    for url in urls:
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in ("-", "_", ".")).rstrip()
        file_path = os.path.join(download_path, safe_file_name)

        logger.info(f"Downloading: {url} to {file_path}")
        try:
            subprocess.run([wget_path, url, "-O", file_path], check=True, capture_output=True, text=True)
            logger.info(f"Successfully downloaded {safe_file_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download {safe_file_name}: {e}")
            logger.error(f"wget output: {e.stdout}")
            logger.error(f"wget error: {e.stderr}")


def download_all_classifier_models(download_path: str):
    config = ClassifierConfig(classifier_storage_path=download_path)
    CoreUtil.sync_classifier_models(config=config)


def main():
    parser = argparse.ArgumentParser(description="CLI Tool for managing tasks")
    parser.add_argument("--status", action="store_true", help="Show the current clinical trials infra status")
    parser.add_argument("--version", "-v", action="version", version=f"{__version__}", help="Show the version of the CLI tool")
    parser.add_argument("--download-protocols", action="store_true", help="Download clinical trial protocols")
    parser.add_argument("--download-path", type=str, default=get_default_classifier_storage_path(), help="Path to download the protocols or the models. Defaults to /tmp (if posix) or else C:\\temp.")
    parser.add_argument("--download-models", action="store_true", help="Download all classifier models")

    args = parser.parse_args()

    if args.status:
        logger.info("Status: The CLI is running.")
    elif args.download_protocols:
        logger.info(f"Downloading protocols to: {args.download_path}")
        download_protocols(args.download_path)
    elif args.download_models:
        logger.info(f"Downloading models to: {args.download_path}")
        download_all_classifier_models(args.download_path)
    else:
        logger.info("Use --status to view the current status or --version to view the version.")


if __name__ == "__main__":
    main()
