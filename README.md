# cdn-explorer

Browse public CDN directory listings as a navigable file tree and download files through a size-capped proxy — so you can explore open HTTP(S) mirrors without manually following links.

## Who it's for

Anyone who needs to inspect or pull assets from public CDN / mirror directory listings (Apache/Nginx auto-indexes, Nginx JSON autoindex): release mirrors, asset hosts, open file servers.

## Features

- Crawl a public `http(s)` URL and return its directory tree (parses Apache/Nginx HTML listings and Nginx JSON autoindex).
- Recursive, same-host crawl with safety limits: depth 5, 500 nodes max, results flagged as `truncated` when capped.
- Per-scan log of what was visited.
- React file-tree UI with multi-select and a scan log view.
- Download proxy that streams files with a 50 MB cap; only `http`/`https` URLs accepted.
- Stateless — no database.

## Architecture

```
cdn-explorer/
├── api/   FastAPI backend (crawler + download proxy)
├── app/   React 19 + Vite + TypeScript frontend
└── tests/ Backend pytest suite
```

The backend exposes `POST /api/explore`, `GET /api/download`, and `GET /health`. Interactive API docs are served at `/docs` when the backend is running.

## Run

Requires Docker and Docker Compose. Common commands are in the `Makefile`:

```bash
make up        # production stack
make up-dev    # dev stack with hot-reload
make down      # stop all containers
make logs      # tail logs
```

Production stack: frontend on `http://localhost:8011`, backend on `http://localhost:8000`.

### Backend without Docker

Requires Python ≥ 3.14.

```bash
make dev                            # install dev deps + pre-commit hooks
uvicorn api.main:app --reload       # serve the API
```

### Frontend without Docker

```bash
cd app
npm install
npm run dev                         # Vite dev server on http://localhost:5173
```

## Tests & quality

```bash
make docker-test       # backend tests in Docker
make docker-test-app   # frontend tests in Docker
make test              # backend pytest (deps installed locally)
make ci                # full local gate: lint + typecheck + test
```

## Configuration

Copy the example env files and adjust as needed. All listed variables are optional.

- Backend — `.env.example` → `.env`: `ALLOWED_ORIGINS`, `DEBUG`, `SENTRY_DSN`, `ENVIRONMENT`, `RELEASE`.
- Frontend — `app/.env.example` → `app/.env`: `VITE_API_URL`, `VITE_SENTRY_DSN`, `VITE_ENVIRONMENT`, `VITE_RELEASE`.

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution workflow
- [CHANGELOG.md](CHANGELOG.md) — release history
- [DECISIONS.md](DECISIONS.md) — architectural decision records
- [AGENTS.md](AGENTS.md) — agent context and constraints

## License

See [LICENSE](LICENSE).
