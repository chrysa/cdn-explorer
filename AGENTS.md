# CDN Explorer — Agent Context

## Purpose

Navigate and download files from public CDN directory listings.

## Architecture

```
cdn-explorer/
├── api/           FastAPI backend (crawler + download proxy)
├── app/           React 19 + Vite frontend
├── tests/         Backend pytest tests
├── Dockerfile     Multi-stage (deps/production/dev/test)
└── docker-compose.yml
```

## Key commands

- `make up` — production stack
- `make up-dev` — dev stack (hot-reload)
- `make docker-test` — backend tests
- `make docker-test-app` — frontend tests

## Constraints

- Stateless — no database
- Max crawl: depth 5, 500 nodes, 50 MB download cap
- Only http/https URLs accepted
