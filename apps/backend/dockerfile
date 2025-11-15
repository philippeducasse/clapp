FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
ARG APP_HOME=/app

FROM base AS deps
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

FROM base AS build
WORKDIR ${APP_HOME}

COPY . .
# RUN .venv/bin/python manage.py collectstatic --noinput

FROM base AS run
WORKDIR ${APP_HOME}

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


COPY --from=build /app/.venv ./.venv
COPY --from=build /app .

RUN addgroup --system --gid 1001 django && \
    adduser --system --uid 1001 --gid 1001 django && \
    chown -R django:django /app

RUN chmod +x /app/entrypoint.sh

USER django

EXPOSE 8000

ENTRYPOINT [ "app/entrypoint.sh" ]