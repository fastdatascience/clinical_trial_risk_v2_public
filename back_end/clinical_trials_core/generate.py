import argparse
from pathlib import Path


def main():
    """
    Running python generate --module drug_processor  the class name will be DrugProcessor.
    """
    parser = argparse.ArgumentParser(description="Generate module structure for clinical trials.")
    parser.add_argument("--module", type=str, required=True, help="The name of the module to create.")

    args = parser.parse_args()
    module_name = args.module

    new_dir_path = Path(f"src/clinicaltrials/{module_name}")

    new_dir_path.mkdir(parents=True, exist_ok=True)

    init_file_path = new_dir_path / "__init__.py"

    class_name = "".join(word.title() for word in module_name.split("_"))

    contents = f"""\
from clinicaltrials.core import BaseProcessor, Document, ClassifierConfig, Page, Metadata, MetadataOption

class {class_name}(BaseProcessor):
    def __init__(self) -> None:
        super().__init__(module_name=__class__.__name__)

    @property
    def metadata(self) -> Metadata:
        return Metadata(id="{module_name}", name="{class_name}", feature_type="yesno",
                        options=[
                            MetadataOption(label="no", value=0),
                            MetadataOption(label="yes", value=1),
                        ]
                        )

    def process(self, document: Document, config: ClassifierConfig | None = None):
        raise NotImplementedError("Subclasses must implement the 'process' method.")

if __name__ == "__main__":
    d = {class_name}()
    document = Document(
        pages=[Page(content="The first cohort of 6 patients received drug TID at morning,", page_number=1)])
    d_result = d.process(document=document)
    print(d_result)
"""

    with open(init_file_path, "w") as init_file:
        init_file.write(contents)

    print(f"Module '{module_name}' created successfully in 'clinicaltrials' directory.")
    print("Don't forget to add your module to __loaded_modules in src/core.py!!!")

    answer = input("Would you like to generate a unit test? Y/n")
    if answer.lower() != "n":
        test_contents = f"""\
import sys
sys.path.append("..")
sys.path.append("../src/")

import unittest

from clinicaltrials.core import ClinicalTrial, Document, Page

ct = ClinicalTrial()

d = ct.get_module("{module_name}")


class Test{class_name}(unittest.TestCase):
    def test_empty(self):
        d_result = d.process(document=Document(pages=[]))
        self.assertEqual(0, d_result["prediction"])

    def test_short(self):
        document = Document(
            pages=[Page(
                content="MRC research laboratories as per study SSP and stored at -70°C or lower in the MRC biobank ",
                page_number=1)])
        d_result = d.process(document=document)
        self.assertEqual(1, d_result["prediction"])


if __name__ == "__main__":
    unittest.main()
    """

        test_file_path = Path("tests") / f"test_{module_name}.py"
        with open(test_file_path, "w") as init_file:
            init_file.write(test_contents)

        print(f"Test case for '{module_name}' created successfully in '{test_file_path}'")

    core_file = "src/clinicaltrials/core.py"
    answer = input("Would you like to add this file to src/clinicaltrials/core.py? Caution: this involves modifying existing Python code. Y/n")
    if answer.lower() != "n":
        with open(core_file, "r") as f:
            orig_lines = list(f)

        for idx, l in enumerate(list(orig_lines)):
            if "__loaded_modules: dict" in l:
                orig_lines[idx - 2] = orig_lines[idx - 2] + f"    from .{module_name} import {class_name}\n"

                for j in range(idx, idx + 100):
                    if "}" in orig_lines[j]:
                        orig_lines[j - 1] = orig_lines[j - 1] + f'        "{module_name}": {class_name},\n'
                        break
                break

        with open(core_file, "w") as f:
            f.write("".join(orig_lines))

        print(f"{core_file} has been updated. Please check there are no syntax errors.")


if __name__ == "__main__":
    main()
