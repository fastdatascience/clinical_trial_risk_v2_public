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

# Clinical Trials

The Clinical Trial Risk Tool is a web application that allows a user to upload a PDF file of a clinical trial protocol (
a plan for how the trial will be run) and it gets bits of information out of the protocol and gets two values:

* The cost prediction - how much in $ will it cost to run this trial?
* The risk - how risky is this trial?

## Built with

[![Made with Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-%5E0.100-009688?style=flat&logo=fastapi&logoColor=009688&link=https://fastapi.tiangolo.com/)](https://fastapi.tiangolo.com/) ![Docker](https://img.shields.io/badge/Docker-gray?style=flat&logo=docker&logoColor=2496ED) [![Poetry](https://img.shields.io/badge/Poetry-gray?style=flat&logo=poetry&link=https://python-poetry.org/)](https://python-poetry.org/)

## Run with Docker

### 1. Clone the repo

```bash
git clone https://github.com/fastdatascience/clinical_trial_risk_v2_public
```

### 2. Environment variables

#### 2.1 Copy .env files

* Copy the file `/back_end/.env.example-docker` to `/back_end/.env`
* Copy the file `/front_end/.env.example-docker` to `/front_end/.env`

#### 2.2 Default user for login

A new user will be created when you run the application for the first time only.
The email for this user is `publicdocker@fastdatascience.com`.
You can find the password at `/back_end/.env`, look for the env `PUBLIC_DOCKER_USER_PASSWORD` and change the default
password set if needed.

### 3. Containers

#### 3.1 Build and start containers

The command below will build, (re)create, attach services to containers, and finally start all containers. The
back-end will be accessible at `http://127.0.0.1:5000` and the front-end will be accessible at `http://127.0.0.1:5173`.

```bash
docker compose up
```

#### 3.2 Stop containers

The command below still stop all running containers.

```bash
docker compose stop
```