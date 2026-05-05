# CDN Explorer — Claude Context

## Purpose

Web app to explore and download files from public CDN directory listings.
Input: a public URL. Output: navigable file tree + download proxy.

## Stack

- **Backend**: FastAPI (Python 3.12) — `api/` package
- **Frontend**: React 19 + Vite + TypeScript — `app/` directory
- **Container**: Docker multi-stage + Docker Compose

## Key files

| Path | Role |
|------|------|
| `api/crawler.py` | Core crawl logic (directory listing detection + recursion) |
| `api/routers/explore.py` | `/api/explore` and `/api/download` endpoints |
| `api/constants.py` | All magic values (depth, extensions, size limits…) |
| `app/src/pages/ExplorePage.tsx` | Main UI page |
| `app/src/components/FileTree.tsx` | Recursive file tree component |

## Run locally

```bash
make up-dev   # docker compose dev stack — hot reload on :5173
make docker-test  # backend tests in Docker
make docker-test-app  # frontend tests in Docker
```

## Constraints

- No database — stateless crawler, everything in memory per request
- Max crawl depth: 5, max nodes: 500 (constants.py)
- Download proxy capped at 50 MB per file
- CORS restricted to configured origins
