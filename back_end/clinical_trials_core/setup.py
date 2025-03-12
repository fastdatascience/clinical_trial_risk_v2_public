"""
MIT License

Copyright (c) 2024 Fast Data Science (https://fastdatascience.com)
Maintainer: Thomas Wood (https://fastdatascience.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clinicaltrials",
    author="Thomas Wood",
    author_email="thomas@fastdatascience.com",
    description="Fast Clinical NLP tool for analysis of clinical trial protocols",
    keywords="clinical trial, protocol, nlp, natural language processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://fastdatascience.com",
    version="1.2.1",
    maintainer="Abdullah Waqar, Thomas Wood",
    maintainer_email="abdullahwaqar@pm.me, thomas@fastdatascience.com",
    project_urls={
        "Documentation": "https://fastdatascience.com",
        "Bug Reports": "https://github.com/fastdatascience/clinical_trial_risk_v2_public/tree/main/src/back_end/clinical_trials_core/issues",
        "Source Code": "https://github.com/fastdatascience/clinical_trial_risk_v2_public/tree/main/src/back_end/clinical_trials_core",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "requests==2.32.3",
        "spacy==3.7.2",
        "numpy==1.26.4",
        "scikit-learn==1.4.0",
        "drug-named-entity-recognition==2.0.4",
        "pycountry==22.1.10",
        "country-named-entity-recognition==0.4",
        "pandas==2.2.0",
        "pdfplumber==0.11.4",
        "pypdf==5.0.0",
        "pydantic==2.10.6",
    ],
    extras_require={
        "dev": ["check-manifest"],
    },
)
