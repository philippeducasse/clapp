# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CAB (Circus Agent Backend) is a Django REST Framework application for managing circus/street performance bookings. The application helps performers track organisations (festivals, venues, residencies), performances, and applications to perform at various events.

## Development Commands

### Package Management
- Install dependencies: `uv sync`
- Install with dev dependencies: `uv sync --dev`

### Running the Application
- Start development server: `python manage.py runserver`
- Run migrations: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`

### Testing
- Run all tests: `uv run pytest`
- Run specific test file: `uv run pytest path/to/test_file.py`
- Run with coverage: `uv run pytest --cov=. --cov-report=html`
- Tests use in-memory SQLite database (configured in conftest.py)

### Code Quality
- Format code: `ruff format .`
- Lint code: `ruff check . --fix`
- Type check: `mypy .`
- Pre-commit hooks: `pre-commit run --all-files`

## Architecture

### Core Domain Models

The application uses Django's model inheritance and generic relations to handle multiple organisation types:

**Abstract Base Models:**
- `Organisation` (organisations/models.py): Abstract base for all organisation types (festivals, venues, residencies)
- `OrganisationContact`: Abstract base for contact information

**Concrete Organisation Types:**
- `Festival` (organisations/festivals/models.py): Extends Organisation with festival-specific fields (dates, application periods)
- `Venue` (organisations/venues/models.py): Extends Organisation with venue-specific fields
- `Residency` (organisations/residencies/models.py): Extends Organisation with residency-specific fields

**Applications & Performances:**
- `Application` (applications/models.py): Uses Django's `GenericForeignKey` to link to any organisation type (Festival, Venue, or Residency). The `content_type` and `object_id` fields enable polymorphic relationships.
- `Performance` (performances/models.py): Represents a show/act with associated dossiers (PDF files)

**User Management:**
- `Profile` (profiles/models.py): Custom user model extending Django's AbstractUser. Uses email as USERNAME_FIELD instead of username. Includes email configuration for sending applications directly from user accounts.

### Generic Relations Pattern

The codebase uses Django's `GenericForeignKey` to enable applications to reference different organisation types:

- On `Application`: `GenericForeignKey` combines `content_type` + `object_id` to point to Festival/Venue/Residency
- On organisation models: `GenericRelation` enables reverse lookups (e.g., `festival.applications.all()`)

This pattern allows a single Application model to work with multiple organisation types without separate tables.

### URL Normalization

All URL fields use the `normalize_url()` utility (circus_agent_backend/utils.py) to automatically add `https://` if no protocol is specified. This happens in model `clean()` methods and via the custom `NormalizedURLField` serializer.

### Services Layer

- `organisations/services.py`: Contains business logic for enriching organisation data using AI services
- `services/gemini_service.py`: Google Gemini API integration for web search and data enrichment
- `services/mistral_service.py`: Mistral AI integration

### Django Apps Structure

- `applications/`: Application tracking and submission
- `performances/`: Performance/show management with PDF dossiers
- `profiles/`: Custom user model with email configuration
- `organisations/`: Base organisation models and shared logic
  - `organisations/festivals/`: Festival-specific models, views, and serializers
  - `organisations/venues/`: Venue-specific models, views, and serializers
  - `organisations/residencies/`: Residency-specific models, views, and serializers

### Settings & Configuration

- Main settings: `circus_agent_backend/settings.py`
- Custom user model: `AUTH_USER_MODEL = "profiles.Profile"`
- Database: SQLite for development (PostgreSQL config commented out)
- CORS configured for frontend running on localhost:3000 and localhost:3020
- REST Framework uses session authentication

### Testing Configuration

- pytest configured with Django plugin (pyproject.toml)
- Tests use separate settings file: `circus_agent_backend/settings_test.py`
- Test database: in-memory SQLite (configured in settings_test.py)
- API keys for Gemini/Mistral set to dummy values in conftest.py for testing
- Coverage configured to exclude tests, migrations, and certain files
- **Important**: All test fixtures that create database objects must include `db` parameter (e.g., `def my_fixture(db):`) to ensure they use the test database