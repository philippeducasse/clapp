# Clapp Backend

[![Tests](https://github.com/philippeducasse/clapp_backend/actions/workflows/tests.yml/badge.svg)](https://github.com/philippeducasse/clapp_backend/actions/workflows/tests.yml)
[![Deploy](https://github.com/philippeducasse/clapp_backend/actions/workflows/deploy.yml/badge.svg)](https://github.com/philippeducasse/clapp_backend/actions/workflows/deploy.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-6.0-green)
![DRF](https://img.shields.io/badge/DRF-3.16-red)

REST API backend for Clapp — a platform managing performer applications and organizational scheduling for freelance artists.

## Stack

- **Framework:** Django 6 + Django REST Framework
- **Database:** PostgreSQL
- **Cache / Queue:** Redis + Celery
- **AI Search:** Mistral AI
- **Auth integrations:** Google OAuth
- **Deployment:** Docker + Gunicorn + Nginx

## Getting started

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env  # fill in your values

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

## Running tests

```bash
uv run pytest
```

Coverage reports are generated in `htmlcov/` automatically.

```

## Deployment

Pushes to the `production` branch trigger the CI pipeline, which:
1. Runs the full test suite
2. Builds and pushes a Docker image to Docker Hub
3. Deploys to the remote server via SSH + docker-compose