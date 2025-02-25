FROM python:3.11-slim AS builder

# Install system dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl unrar-free

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

# Copy app
COPY . .

# Download models and demo user data
RUN mkdir /tmp/models/
RUN mkdir /tmp/demo_user_data/
RUN . /venv/bin/activate; \
    $POETRY_HOME/bin/poetry run python cli --download-models --download-path /tmp/models/ \
    && $POETRY_HOME/bin/poetry run python cli --download-demo-user-data --download-path /tmp/

# ---------------------------------------------------------

FROM python:3.11-slim AS final

# Install wkhtmltopdf
RUN apt-get update && apt-get install -y wkhtmltopdf xxd

# Create storage dir for local storage
RUN mkdir -p /tmp/storage
RUN chown -R nobody:nogroup /tmp/storage

# Set user
USER nobody

# Set work dir
WORKDIR /app

# Create /tmp/envfile with envrionemnts to load on startup
RUN echo "export INIT_DEMO_USER_USER_RESOURCE_IDENTIFIER=`head -c 16 /dev/urandom | xxd -p`" >> /tmp/envfile

# Copy environment from builder stage
COPY --from=builder /venv /venv

# Copy app from builder stage
COPY --from=builder --chown=nobody:nogroup /app/ .

# Copy models from builder stage
COPY --from=builder --chown=nobody:nogroup /tmp/models/ /tmp/

# Copy demo user data from builder stage
RUN mkdir /tmp/demo_user_data
COPY --from=builder --chown=nobody:nogroup /tmp/demo_user_data/ /tmp/demo_user_data/
RUN . /tmp/envfile && mkdir -p /tmp/storage/cdn/documents/$INIT_DEMO_USER_USER_RESOURCE_IDENTIFIER
RUN . /tmp/envfile && cp -a /tmp/demo_user_data/documents/* /tmp/storage/cdn/documents/$INIT_DEMO_USER_USER_RESOURCE_IDENTIFIER/

# Set environment path
ENV PATH=/venv/bin:${PATH}
