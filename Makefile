SHELL := /bin/bash

.PHONY: dev backend frontend help

help:
	@echo "Available targets:"
	@echo "  make dev       - Run backend and frontend concurrently"
	@echo "  make backend   - Run backend only"
	@echo "  make frontend  - Run frontend only"

dev:
	@echo "Starting backend and frontend servers..."
	@trap 'kill 0' EXIT; \
	(cd apps/backend && source .venv/bin/activate && python manage.py runserver) & \
	(cd apps/frontend && pnpm run dev) & \
	wait

backend:
	@cd apps/backend && source .venv/bin/activate && python manage.py runserver

frontend:
	@cd apps/frontend && npm run dev