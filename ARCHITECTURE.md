# Architecture — cdn-explorer

## Purpose

`cdn-explorer` is a small full-stack tool that crawls a public directory-listing
URL (nginx/Apache autoindex and nginx JSON autoindex are detected), builds a file
tree from the assets it finds, and lets you download individual files through a
size-capped proxy. It is stateless: nothing is persisted, every crawl runs in
memory per request. Traversal is bounded (same-host only, max depth 5, max 500
nodes) and the download proxy accepts only `http`/`https` with a 50 MB cap.

## Stack

- **Backend**: Python 3.14, FastAPI, Pydantic v2 / pydantic-settings, httpx,
  BeautifulSoup4, uvicorn; Sentry (`sentry-sdk[fastapi]`, optional).
- **Frontend**: React + TypeScript, Vite. Tests via Vitest.
- **Tooling (backend)**: Ruff, mypy, pytest (+ pytest-asyncio, pytest-cov),
  pre-commit. Config lives in `pyproject.toml`.
- **Container**: Docker + Docker Compose (prod `docker-compose.yml`, dev
  `docker-compose.dev.yml`); test/lint image built from `Dockerfile`.
- No database — stateless crawler, in-memory per request.

## Layout

- `api/` — FastAPI backend.
  - `main.py` — app factory, CORS, router include, `/health` probe.
  - `config.py` — settings (`DEMO_MODE`, Sentry, CORS origins).
  - `crawler.py` — directory-listing crawl / tree building.
  - `ssrf.py` — SSRF guard (same-host, scheme checks).
  - `fixtures.py` — demo-mode fixture data.
  - `schemas.py`, `constants.py` — models and bounds.
  - `routers/explore.py` — `/api/explore` and download proxy routes.
  - `observability/` — Sentry init.
- `app/` — React/Vite frontend (`src/pages/ExplorePage.tsx`,
  `components/FileTree.tsx`, `ScanLog.tsx`, `DemoBanner.tsx`, `api/client.ts`,
  `domain/types.ts`). Design notes in `app/DESIGN.md` and
  `app/design-system/`.
- `tests/` — backend pytest suite (crawler, explore, ssrf, demo-mode).
- `scripts/` — `gen_context_files.py`, `quality_gate.py`.
- Root — `Dockerfile`, `docker-compose*.yml`, `Makefile`, `pyproject.toml`.

## Entrypoints

- **Backend**: `api.main:app` (FastAPI), served by uvicorn in-container.
- **Frontend**: `app/src/main.tsx` → `App.tsx`, built/served by Vite.
- **HTTP routes**:
  - `POST /api/explore` — crawl a URL → `{ root_url, total_nodes, tree, truncated, log }`.
  - Download proxy route (streams a file through the backend; `http`/`https` only, 50 MB cap).
  - `GET /health` — liveness probe, also reports `demo_mode`.

## Data / External deps

- **No persistent storage** — every crawl is per-request and in memory.
- **External**: fetches the user-supplied public CDN/open-directory URL over
  HTTP(S) via httpx (bounded, same-host, SSRF-guarded).
- **Sentry** — optional error tracking (`SENTRY_DSN`, off if blank).
- **Env** (`.env.example`): `DEMO_MODE` (serve fixtures, no real CDN; shows a
  DEMO banner), `SENTRY_DSN`, `ENVIRONMENT`, `RELEASE`.

## Build & test

Real commands (from `Makefile`; targets build/use the in-container image — no
host pip/venv):

```bash
make up               # start production stack (compose)
make up-dev           # dev stack, frontend hot-reload on :5173
make down             # stop all containers
make build            # build all images
make lint             # ruff (in-container)
make format           # ruff format (in-container)
make typecheck        # mypy (in-container)
make test             # backend pytest (in-container)
make test-cov         # pytest with coverage (fail-under 85%)
make docker-test      # backend tests in Docker
make docker-test-app  # frontend tests (Vitest) in Docker
make pre-commit       # run pre-commit on all files
make ci               # lint + typecheck + test
```

Ports (prod compose): frontend `5173`, API `8010:8000`, `8011:80`.
Frontend package scripts (`app/package.json`): `dev`, `build`
(`tsc -b && vite build`), `test` (`vitest run --coverage`), `lint`, `typecheck`.
