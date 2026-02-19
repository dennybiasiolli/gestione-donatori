# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gestione Donatori** is a Django web application for managing blood donors in AVIS (Italian blood donor association) sections. It handles donor records, donation tracking, statistical reporting, and Excel exports.

## Common Commands

```bash
# Install dependencies (requires UV)
make requirements

# Download Bootstrap & Bootstrap Icons static assets
make get-static-libs

# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Load sample data
python manage.py loaddata avis

# Run tests (with coverage, stops on first failure)
make tests
# or: uv run pytest

# Run a single test file or test
uv run pytest avis/tests/test_views.py
uv run pytest avis/tests/test_views.py::TestDonatore::test_list

# Check code style (black, isort, flake8)
make style-check

# Auto-fix style issues
make style-fix

# Set up optional git hooks (pre-commit style check, pre-push tests)
make githooks
```

## Architecture

### App Structure

The project has a single Django app (`avis/`) within a `website/` project config:

- `website/` — Django project config (settings, root URLs, wsgi/asgi)
- `avis/` — Main app (models, views, urls, forms, templates, static files, tests)

### Multi-tenant Design

The `Sezione` (section) model is the tenant anchor. Each Django user is linked to one or more sections. All donor data is scoped to a section. Superusers see all sections; staff see only their assigned section(s). Access is gated by `avis_user_check` (staff-only).

### Core Models

- **Sezione** — Blood donor section/chapter; links to a staff user, stores award thresholds (PostgreSQL `ArrayField`)
- **Sesso** — Gender type with donation interval rules (whole blood, plasma, platelets)
- **StatoDonatore** — Donor status (active/inactive); can be section-specific or global
- **Donatore** — Individual donor with personal info, blood type, privacy consent; changes are tracked via `django-reversion`
- **Donazione** — Individual donation record; unique constraint on (donor, date)

### URL Structure

```
/                          → redirects to /donatori/
/accounts/login/           → authentication
/donatori/                 → donor list with search/filter and print options
/donatori/<id>/            → donor detail with donation history
/donatori/<id>/nuova-donazione/ → add donation
/dati-statistici/          → statistical reports
/export-elenco-soci/       → Excel export
/amministrazione-donatori/ → Django admin (URL configurable via env)
```

### Key Technologies

- **Django 5.2+** with `django-filter` for list filtering and `django-reversion` for audit history
- **PostgreSQL** in production (uses `ArrayField`); SQLite works for development
- **UV** as the Python package manager (not pip)
- **openpyxl** for Excel exports
- **Bootstrap 5.3.2** (downloaded locally via `make get-static-libs`)
- **pytest-django** + **pytest-cov** for testing

### Settings & Environment

Copy `.env.default` to `.env` and adjust values. Key variables: `DEBUG`, `SECRET_KEY`, `DB_*` (database connection), `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `ADMIN_BASE_URL`.

Settings split: `website/settings_base.py` (all config) + `website/settings.py` (loads `.env` via python-dotenv).

### Code Style

Black (line length 88) + isort (Black profile) + flake8. CI enforces `make style-check` before tests.

### CI

GitHub Actions (`.github/workflows/django.yml`) runs on push/PR to `main`: installs deps, checks style, runs full test suite against PostgreSQL.
