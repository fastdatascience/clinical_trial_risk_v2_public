![Fast Data Science logo](https://raw.githubusercontent.com/fastdatascience/brand/main/primary_logo.svg)

<a href="https://fastdatascience.com"><span align="left">🌐 fastdatascience.com</span></a>
<a href="https://www.linkedin.com/company/fastdatascience/"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/linkedin.svg" alt="Fast Data Science | LinkedIn" width="21px"/></a>
<a href="https://twitter.com/fastdatascienc1"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/x.svg" alt="Fast Data Science | X" width="21px"/></a>
<a href="https://www.instagram.com/fastdatascience/"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/instagram.svg" alt="Fast Data Science | Instagram" width="21px"/></a>
<a href="https://www.facebook.com/fastdatascienceltd"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/fb.svg" alt="Fast Data Science | Facebook" width="21px"/></a>
<a href="https://www.youtube.com/channel/UCLPrDH7SoRT55F6i50xMg5g"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/yt.svg" alt="Fast Data Science | YouTube" width="21px"/></a>
<a href="https://g.page/fast-data-science"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/google.svg" alt="Fast Data Science | Google" width="21px"/></a>
<a href="https://medium.com/fast-data-science"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/medium.svg" alt="Fast Data Science | Medium" width="21px"/></a>
<a href="https://mastodon.social/@fastdatascience"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/mastodon.svg" alt="Fast Data Science | Mastodon" width="21px"/></a>

# Fast Clinical NLP Python Library - analysis of clinical trial protocols

## Where everything is

New version at: https://clinical.fastdatascience.com/login

Old version at: https://app.clinicaltrialrisk.org/

# What does the Fast Clinical NLP do?

* It's hard to determine the cost of a clinical trial
* Relevant information is stored in plain text
* The tool uses NLP to extract data from the tool

## Requirements

You need a Windows, Linux or Mac system with

* Python 3.11 or above
* Java 17 (if you want to extract items from PDFs)
* the requirements in [requirements.txt](./requirements.txt)

## Who to contact?

You can contact Thomas Wood at https://fastdatascience.com/.


## 🖥 Installing the Python package

```
pip install .
```

## Working in this environment

We recommend making a virtual environment:

```
python -m venv venv
source venv/bin/activate
```


## Developing the tool

### How to generate a new module

```
python generate.py --module test_module
```

### 🧪 Automated tests

Test code is in **tests/** folder using [unittest](https://docs.python.org/3/library/unittest.html).

The testing tool `tox` is used in the automation with GitHub Actions CI/CD. **Since the PDF extraction also needs Java and Tika installed, you cannot run the unit tests without first installing Java and Tika. See above for instructions.**

### 🧪 Use tox locally

Install tox and run it:

```
pip install tox
tox
```

In our configuration, tox runs a check of source distribution using [check-manifest](https://pypi.org/project/check-manifest/) (which requires your repo to be git-initialized (`git init`) and added (`git add .`) at least), setuptools's check, and unit tests using pytest. You don't need to install check-manifest and pytest though, tox will install them in a separate environment.

The automated tests are run against several Python versions, but on your machine, you might be using only one version of Python, if that is Python 3.9, then run:

```
tox -e py39
```

Thanks to GitHub Actions' automated process, you don't need to generate distribution files locally.

## News: Dash in Action webinar on 7 June 2023

![The Dash App webinar](screenshots/1684787269147.png)

Thomas Wood of [Fast Data Science](http://fastdatascience.com/) presented this tool at the [Plotly](https://plotly.com/) [Dash in Action webinar](https://go.plotly.com/dash-in-action), showing how the app uses [Natural Language Processing](https://naturallanguageprocessing.com) to estimate the risk of a clinical trial failing.

[![The Dash App webinar](/screenshots/video.jpg)](https://youtu.be/KL8cytV1qRA?t=2111 "The Dash App webinar")


## 📜 License

MIT License. Copyright (c) 2024 Fast Data Science (https://fastdatascience.com)

## How to cite the Fast Clinical NLP Python Library?

If you would like to cite the tool alone, you can cite:

Wood TA and McNair D. [Clinical Trial Risk Tool](https://fastdatascience.com/clinical-trial-risk-tool/): software application using natural language processing to identify the risk of trial uninformativeness. Gates Open Res 2023, 7:56 doi: [10.12688/gatesopenres.14416.1](https://gatesopenresearch.org/articles/7-56).

A BibTeX entry for LaTeX users is

```
@article{Wood_2023,
	doi = {10.12688/gatesopenres.14416.1},
	url = {https://doi.org/10.12688%2Fgatesopenres.14416.1},
	year = 2023,
	month = {apr},
	publisher = {F1000 Research Ltd},
	volume = {7},
	pages = {56},
	author = {Thomas A Wood and Douglas McNair},
	title = {Clinical Trial Risk Tool: software application using natural language processing to identify the risk of trial uninformativeness},
	journal = {Gates Open Research}
}
```
