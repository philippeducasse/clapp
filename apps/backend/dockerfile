FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS python-build-stage

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN uv sync --no-dev

COPY . /app/