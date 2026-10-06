# Testing — cdn-explorer

> Tags: **FACT** = verified in the repo. Commands below are copied from the
> `Makefile` and `app/package.json`; run them in-container per repo policy (never
> host `pytest`/`ruff`/`mypy` directly).

## How to run

| Command | What it runs | Source |
| --- | --- | --- |
| `make ci` | lint + typecheck + backend test | `Makefile` |
| `make test` | backend pytest (in-container) | `Makefile` |
| `make test-cov` | pytest with coverage, `--cov-fail-under=85` | `Makefile`, `pyproject.toml` |
| `make docker-test` | backend tests in Docker | `Makefile` |
| `make docker-test-app` | frontend tests (Vitest) in Docker | `Makefile` |
| `make lint` / `make typecheck` / `make format` | Ruff / mypy / Ruff format | `Makefile` |
| `pre-commit run --all-files` | full pre-commit gate | `CONTRIBUTING.md` |

Coverage gate: **85%** on `api` (`--cov-fail-under=85`, `--cov=api`). **FACT.**

## Backend suite (`tests/`, pytest + pytest-asyncio)

| File | Focus | Notable cases (**FACT**, from test names) |
| --- | --- | --- |
| `tests/test_crawler.py` | crawl/listing logic | skippable-href handling (parent/self/root/anchor/query/mailto/normal/subdir), `is_asset` (pdf yes, html yes, php no), directory-listing detection, URL normalize, same-host true/false, crawl of HTML listing, recursion into subdirs, truncation still returns nodes, nginx-JSON parse valid/not-json/wrong-shape, crawl nginx-JSON listing |
| `tests/test_explore.py` | `/api/explore` + `/api/download` | health, explore returns tree, invalid URL, missing URL, truncated, nested tree; download invalid scheme, **blocks private target**, success, upstream error, **file too large** |
| `tests/test_ssrf.py` | SSRF guard | public URL allowed, private IP blocked (parametrized), non-http scheme blocked, unresolvable host blocked, mixed public+private blocked |
| `tests/test_demo_mode.py` | demo mode | health reports `demo_mode`, explore returns fixtures without network, download returns inline demo payload |

Fixtures/config: `tests/conftest.py` provides an async `client` (httpx `AsyncClient`).
**FACT.**

## Frontend suite (`app/src/__tests__/`, Vitest + Testing Library)

- `DemoBanner.test.tsx` — renders the amber DEMO banner when demo mode is active;
  renders nothing when off.
- `ExplorePage.test.tsx` — renders the URL input; shows results after exploring.

Frontend coverage is collected (`vitest run --coverage`, `app/package.json`). **FACT.**

## Mutation testing

`.github/workflows/mutation-testing.yml` exists — a mutation-testing workflow runs in
CI. **FACT.** (Config/threshold detail: **UNKNOWN** from this pass.)

## Gaps / notes

- No load/performance test is present. **FACT.**
- The SSRF DNS-rebinding (TOCTOU) case and redirect re-validation (see `SECURITY.md`)
  are not covered by an explicit test in the names read. **INFERENCE.**
