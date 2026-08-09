# cdn-explorer

> Explore and download files from public CDN / open directory listings.
> Give it a public URL, get back a navigable file tree — then proxy-download any file.

## Overview

`cdn-explorer` is a small full-stack tool that crawls a public directory-listing
URL (nginx/Apache autoindex and nginx JSON autoindex are detected), builds a file
tree from the assets it finds, and lets you download individual files through a
size-capped proxy. It is stateless: nothing is persisted, every crawl runs in
memory per request.

- **Backend** — FastAPI (Python 3.14), `api/` package.
- **Frontend** — React 19 + TypeScript + Vite, `app/` directory.
- **Container** — Docker + Docker Compose (prod and dev stacks).

## Features

| Area | What it does |
| --- | --- |
| Directory crawl | Detects HTML autoindex listings and nginx JSON autoindex, recurses into sub-directories |
| Asset filtering | Keeps known downloadable extensions (documents, archives, media, web assets, fonts…) — see `api/constants.py` |
| Bounded traversal | Same-host only, max depth 5, max 500 nodes, per-request crawl log + `truncated` flag |
| Download proxy | Streams a file through the backend; `http`/`https` only, 50 MB cap, explicit timeouts |
| Demo mode | `DEMO_MODE=true` serves fixture data so the app is fully explorable without hitting any real CDN |

## API

| Method / path | Purpose |
| --- | --- |
| `POST /api/explore` | Crawl a URL → `{ root_url, total_nodes, tree, truncated, log }` |
| `GET /api/download?url=…` | Proxy-download a single public file (scheme-checked, size-capped, streamed) |

## Run locally

```bash
make up-dev          # dev stack, frontend hot-reload on :5173
make up              # production stack
make docker-test     # backend tests in Docker
make docker-test-app # frontend tests in Docker
make ci              # lint + typecheck + test (backend)
```

## Layout

| Path | Role |
| --- | --- |
| `api/crawler.py` | Crawl logic — listing detection, nginx-JSON parsing, recursion, same-host guard |
| `api/routers/explore.py` | `/api/explore` and `/api/download` endpoints |
| `api/constants.py` | Crawl bounds, asset extensions, download cap, timeouts, user-agent |
| `api/config.py` | Env-based settings (allowed origins, demo mode) |
| `app/src/pages/ExplorePage.tsx` | Main UI page |
| `app/src/components/FileTree.tsx` | Recursive file-tree component |

## Constraints

- No database — stateless crawler, in-memory per request.
- Crawl bounded to depth 5 / 500 nodes, same host only.
- Download proxy: `http`/`https` schemes only, 50 MB per file.
- CORS restricted to configured origins (`api/config.py`).
