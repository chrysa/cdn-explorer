# CDN Explorer — Claude Context

> **Claude Code**: also read `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` for code specifications.

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

## Skills

Shared skills from `shared-standards/.claude/skills/`:
- `ui-ux/SKILL.md` — UX/UI/ergonomics across ALL surfaces (web, CLI, VS Code, Discord, desktop, game, agent) + WCAG 2.1 AA + dark mode + i18n FR+EN (load when building any human-facing surface)
