# Requirements — cdn-explorer

> Derived from the code and existing docs. `IMPLEMENTED` is asserted only where
> verifiable in the repo (source file and/or a passing-named test). Tags:
> **FACT** / **INFERENCE** / **UNKNOWN**.

## Product requirements (REQ-PROD)

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| REQ-PROD-001 | Given a public directory-listing URL, return a navigable file tree | IMPLEMENTED | `api/crawler.py`, `POST /api/explore`, `tests/test_explore.py::test_explore_returns_tree` |
| REQ-PROD-002 | Detect HTML autoindex (nginx/Apache) and nginx JSON autoindex listings | IMPLEMENTED | `api/crawler.py`, `tests/test_crawler.py` (directory-listing + nginx-JSON cases) |
| REQ-PROD-003 | Recurse into sub-directories, same host only | IMPLEMENTED | `api/crawler.py` (`_same_host`), `tests/test_crawler.py::test_crawl_non_listing_follows_subdirs` / `test_same_host_*` |
| REQ-PROD-004 | Keep only known downloadable asset extensions | IMPLEMENTED | `api/constants.py`, `tests/test_crawler.py::test_is_asset_*` |
| REQ-PROD-005 | Proxy-download a single chosen public file, streamed | IMPLEMENTED | `GET /api/download`, `tests/test_explore.py::test_download_success` |
| REQ-PROD-006 | Signal truncation when crawl bounds are hit | IMPLEMENTED | `truncated` flag + `log`, `tests/test_crawler.py::test_crawl_truncated_still_returns_nodes` |
| REQ-PROD-007 | Demo mode serves fixtures without contacting any real CDN | IMPLEMENTED | `api/fixtures.py`, `DEMO_MODE`, `tests/test_demo_mode.py` |
| REQ-PROD-008 | Frontend shows a persistent DEMO banner while demo mode is on | IMPLEMENTED | `app/src/components/DemoBanner.tsx`, `DemoBanner.test.tsx` |
| REQ-PROD-009 | Frontend renders a recursive file tree and a scan log | IMPLEMENTED | `app/src/components/FileTree.tsx`, `ScanLog.tsx`, `ExplorePage.test.tsx` |

## Technical requirements (REQ-TECH)

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| REQ-TECH-001 | Reject non-public / SSRF targets (private, loopback, link-local, unresolvable) | IMPLEMENTED | `api/ssrf.py`, `tests/test_ssrf.py`, `test_download_blocks_private_target` |
| REQ-TECH-002 | Accept `http`/`https` schemes only | IMPLEMENTED | `api/ssrf.py`, `api/schemas.py`, `tests/test_ssrf.py::test_non_http_scheme_is_blocked`, `test_download_invalid_scheme` |
| REQ-TECH-003 | Bound crawl: depth ≤ 5, ≤ 500 nodes | IMPLEMENTED | `api/constants.py`, `api/crawler.py` |
| REQ-TECH-004 | Cap download at 50 MB, abort stream when exceeded | IMPLEMENTED | `MAX_DOWNLOAD_BYTES`, `api/routers/explore.py`, `test_download_file_too_large` |
| REQ-TECH-005 | Explicit outbound HTTP timeouts | IMPLEMENTED | `api/constants.py` (INFERENCE — value read via ARCHITECTURE) |
| REQ-TECH-006 | CORS restricted to configured origins | IMPLEMENTED | `api/config.py`, `api/main.py` |
| REQ-TECH-007 | Stateless — no persistence | IMPLEMENTED | no DB anywhere in `api/` (FACT, absence) |
| REQ-TECH-008 | Backend coverage ≥ 85% enforced | IMPLEMENTED | `pyproject.toml` (`--cov-fail-under=85`) |
| REQ-TECH-009 | Return upstream errors as `502` | IMPLEMENTED | `api/routers/explore.py`, `test_download_upstream_error` |
| REQ-TECH-010 | Optional Sentry error tracking, env-gated | IMPLEMENTED | `api/observability/`, `SENTRY_DSN` |

No formal, numbered requirement source exists in the repo; the above is reconstructed
from code + docs. **INFERENCE.**
