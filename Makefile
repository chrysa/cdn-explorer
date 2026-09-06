# makefile-tier: python-app
.DEFAULT_GOAL := help

COMPOSE        := docker compose
COMPOSE_DEV    := docker compose -f docker-compose.yml -f docker-compose.dev.yml
API_IMAGE      := cdn-explorer-api
APP_IMAGE      := cdn-explorer-app

# ── Artifact isolation: keep tool caches out of the repo tree ─────────────────
PROJECT_NAME   ?= cdn-explorer
UID ?= $(shell id -u)
GID ?= $(shell id -g)
_CACHE_BASE ?= $(if $(XDG_CACHE_HOME),$(XDG_CACHE_HOME),$(HOME)/.cache)/chrysa/$(PROJECT_NAME)
RUFF_CACHE_DIR ?= $(_CACHE_BASE)/ruff
MYPY_CACHE_DIR ?= $(_CACHE_BASE)/mypy
PYTHONPYCACHEPREFIX ?= $(_CACHE_BASE)/pycache
PYTEST_ADDOPTS ?= -p no:cacheprovider
export UID GID RUFF_CACHE_DIR MYPY_CACHE_DIR PYTHONPYCACHEPREFIX PYTEST_ADDOPTS

.PHONY: help up up-dev down build test test-cov lint format typecheck pre-commit \
        install dev build-test-image docker-test docker-test-app docker-up \
        docker-down ci logs clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ────────────────────────────────────────────────────────────────────

up: ## Start production stack
	$(COMPOSE) up -d --build

up-dev: ## Start dev stack (hot-reload)
	$(COMPOSE_DEV) up --build

down: ## Stop all containers
	$(COMPOSE) down

docker-up: up ## Alias for up
docker-down: down ## Alias for down

build: ## Build all images
	docker build --target production -t $(API_IMAGE):latest .
	docker build --target production -t $(APP_IMAGE):latest ./app

build-test-image: ## Build the in-container backend dev/test image (ruff, mypy, pytest)
	docker build --target test -t $(API_IMAGE):test .

docker-test: build-test-image ## Run backend tests inside Docker
	docker run --rm $(API_IMAGE):test

docker-test-app: ## Run frontend tests inside Docker
	docker build --target test -t $(APP_IMAGE):test ./app
	docker run --rm $(APP_IMAGE):test

logs: ## Tail all container logs
	$(COMPOSE) logs -f

# ── Quality ───────────────────────────────────────────────────────────────────

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

lint: build-test-image ## Lint backend (ruff, in-container)
	docker run --rm $(API_IMAGE):test ruff check api tests

format: build-test-image ## Format backend (ruff, in-container)
	docker run --rm -v "$(CURDIR):/work" -w /work $(API_IMAGE):test ruff format api tests

typecheck: build-test-image ## Type-check backend (mypy, in-container)
	docker run --rm $(API_IMAGE):test mypy api

test: build-test-image ## Run backend tests (in-container)
	docker run --rm $(API_IMAGE):test pytest

install: build-test-image ## Build the in-container backend dev image (no host pip)
	@echo "✓ In-container dev image ready ($(API_IMAGE):test). Run the loop with: make dev / make test / make lint"

dev: build-test-image ## Build the in-container dev image and install pre-commit hooks
	pre-commit install

test-cov: build-test-image ## Run tests with coverage report (in-container)
	docker run --rm -v "$(CURDIR)/reports:/app/reports" $(API_IMAGE):test \
		pytest --cov=api --cov-branch \
		--cov-report=xml:reports/coverage.xml \
		--cov-report=html:reports/coverage_html_report \
		--cov-fail-under=85

# ── Misc ──────────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml app/dist

# ─── CI gate ────────────────────────────────────
ci: lint typecheck test ## Run the full local gate (lint + typecheck + test)
