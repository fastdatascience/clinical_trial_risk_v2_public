FROM python:3.11-slim AS builder

# Install system dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl

# Create environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m venv /venv

# Install Poetry
ENV POETRY_VERSION=1.8.5
ENV POETRY_HOME=/opt/poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl https://install.python-poetry.org | python -

# Set work dir
WORKDIR /app

# Copy app dependencies
COPY pyproject.toml poetry.lock ./

# Copy clinical_trials_core
COPY ./clinical_trials_core ./clinical_trials_core

# Activate environment and install dependencies
RUN . /venv/bin/activate; \
    $POETRY_HOME/bin/poetry lock --no-update \
    && $POETRY_HOME/bin/poetry install --only main --no-interaction \
    && $POETRY_HOME/bin/poetry update clinicaltrials

# ---------------------------------------------------------

FROM python:3.11-slim AS final

# Copy environment from builder stage
COPY --from=builder /venv /venv

# Set environment path
ENV PATH=/venv/bin:${PATH}

# Install wkhtmltopdf
RUN apt-get update && apt-get install -y wkhtmltopdf

# Set work dir
WORKDIR /app

# Set user
USER nobody

# Copy classifiers
COPY ./classifiers /tmp

# Copy app
COPY --chown=nobody:nogroup hypercorn.toml .
COPY --chown=nobody:nogroup . .
