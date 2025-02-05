# Generate the requirements.txt from setup.py

import re

requirements = []
is_in_requirements = False
with open("setup.py", "r") as f:
    for l in f:
        if "]," in l:
            is_in_requirements = False
        if is_in_requirements:
            l = re.sub(r'\'|"|,$', "", l.strip()).strip()
            requirements.append(l)

        if "install_requires" in l:
            is_in_requirements = True

with open("requirements.txt", "w") as f:
    f.write("\n".join(requirements))
