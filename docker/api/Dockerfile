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
COPY back_end/pyproject.toml back_end/poetry.lock ./

# Copy clinical_trials_core
COPY back_end/clinical_trials_core ./clinical_trials_core

# Activate environment and install dependencies
RUN . /venv/bin/activate; \
    $POETRY_HOME/bin/poetry lock --no-update \
    && $POETRY_HOME/bin/poetry install --only main --no-interaction \
    && $POETRY_HOME/bin/poetry update clinicaltrials

# Copy app
COPY back_end/ .

# Download models
RUN mkdir /tmp/models/
RUN . /venv/bin/activate; \
    $POETRY_HOME/bin/poetry run python cli --download-models --download-path /tmp/models/

# ---------------------------------------------------------

FROM python:3.11-slim AS final

# Install wkhtmltopdf
RUN apt-get update && apt-get install -y wkhtmltopdf

# Set user
USER nobody

# Set work dir
WORKDIR /app

# Copy environment from builder stage
COPY --from=builder /venv /venv

# Copy app from builder stage
COPY --from=builder --chown=nobody:nogroup /app/ .

# Copy models from builder stage
COPY --from=builder --chown=nobody:nogroup /tmp/models/ /tmp/

# Set environment path
ENV PATH=/venv/bin:${PATH}
