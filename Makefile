.DEFAULT_GOAL := help

COMPOSE        := docker compose
COMPOSE_DEV    := docker compose -f docker-compose.yml -f docker-compose.dev.yml
API_IMAGE      := cdn-explorer-api
APP_IMAGE      := cdn-explorer-app

.PHONY: help up up-dev down build test lint format typecheck pre-commit \
        docker-test docker-test-app logs clean

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

docker-test: ## Run backend tests inside Docker
	docker build --target test -t $(API_IMAGE):test .
	docker run --rm $(API_IMAGE):test

docker-test-app: ## Run frontend tests inside Docker
	docker build --target test -t $(APP_IMAGE):test ./app
	docker run --rm $(APP_IMAGE):test

logs: ## Tail all container logs
	$(COMPOSE) logs -f

# ── Quality ───────────────────────────────────────────────────────────────────

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

lint: ## Lint backend (ruff)
	ruff check api tests

format: ## Format backend (ruff)
	ruff format api tests

typecheck: ## Type-check backend (mypy)
	mypy api

test: ## Run backend tests (requires deps installed)
	pytest

install: ## Install backend dev dependencies
	pip install -e ".[dev]"

dev: install ## Install dev dependencies and pre-commit hooks
	pre-commit install

test-cov: ## Run tests with coverage report
	pytest --cov=api --cov-branch \
		--cov-report=xml:reports/coverage.xml \
		--cov-report=html:reports/coverage_html_report \
		--cov-fail-under=85

# ── Misc ──────────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml app/dist
