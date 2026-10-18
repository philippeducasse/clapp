SHELL := /bin/bash

.PHONY: dev backend frontend discovery help

help:
	@echo "Available targets:"
	@echo "  make dev       - Run backend, frontend and discovery concurrently"
	@echo "  make backend   - Run backend only"
	@echo "  make frontend  - Run frontend only"
	@echo "  make discovery - Run discovery service only (port 8001)"

dev:
	@echo "Starting backend, frontend and discovery servers..."
	@trap 'kill 0' EXIT; \
	(cd apps/backend && source .venv/bin/activate && python manage.py migrate && python manage.py runserver) & \
	(cd apps/frontend && pnpm run dev) & \
# 	(cd apps/discovery && env -u VIRTUAL_ENV uv run fastapi run discovery/app.py --port 8001) & \
	wait

backend:
	@cd apps/backend && source .venv/bin/activate && python manage.py runserver

frontend:
	@cd apps/frontend && npm run dev

# `fastapi run`, not `fastapi dev`: a reload cancels the active run.
discovery:
	@cd apps/discovery && env -u VIRTUAL_ENV uv run fastapi run discovery/app.py --port 8001
