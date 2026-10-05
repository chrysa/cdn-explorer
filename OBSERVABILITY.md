# Observability — cdn-explorer

> Tags: **FACT** = verified in the repo, **UNKNOWN** = not determinable from this pass.

## Health / liveness

- `GET /health` returns `{"status": "ok", "demo_mode": <bool>}`. It is a liveness probe
  and also reports whether demo mode is active. **FACT** (`api/main.py`).

## Error tracking (Sentry)

- Sentry is integrated via `sentry-sdk[fastapi]`, initialised from
  `api/observability/`. It is **optional** and **off when `SENTRY_DSN` is blank**.
  **FACT** (ARCHITECTURE, `.env.example`, `api/config.py`).
- Configuration env vars: `SENTRY_DSN`, `ENVIRONMENT`, `RELEASE`
  (`RELEASE` default in `.env.example`: `cdn-explorer@0.1.0`). **FACT.**

## Logging

- The download proxy logs a warning when a stream exceeds `MAX_DOWNLOAD_BYTES` and
  aborts. **FACT** (`api/routers/explore.py`).
- Each crawl accumulates a per-request `log` (list of strings) returned in the
  `/api/explore` response, plus a `truncated` flag when bounds are hit — this is
  user-facing crawl observability surfaced in the UI (`ScanLog`). **FACT.**
- Structured-logging configuration / log level / format: **UNKNOWN** from this pass.

## Metrics / tracing

- No metrics endpoint (e.g. Prometheus) or distributed tracing was found in the files
  read. **FACT (absence).**

## Deployment visibility

- `.github/workflows/deploy.yml` and `pages.yml` exist (deploy + GitHub Pages).
  Deployment target details: **UNKNOWN** from this pass.
- Container is versioned separately from the app (`GitVersion.yml`, `cliff.toml`).
  **FACT.**

## Standards alignment

The chrysa canon requires `STD-OPS-001` observability and an error-tracking →
GitHub-issues norm (see CLAUDE.md standards block). Sentry error tracking is present;
whether the Sentry→GitHub-issue automation is wired is **UNKNOWN** from this pass.
