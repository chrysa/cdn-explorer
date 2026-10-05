# Security — cdn-explorer

> Scope: this document describes the security posture of the code as it exists in
> the repository. Tags: **FACT** (verified in the repo), **INFERENCE** (reasoned
> from the code), **UNKNOWN** (not determinable from the repo). This tool takes a
> user-supplied URL and fetches it server-side, so SSRF and the download proxy are
> the primary risk surfaces. Owner review requested where flagged.

## Threat model (summary)

`cdn-explorer` accepts an arbitrary public URL from the client, fetches it from the
backend, recurses through directory listings, and can stream a chosen file back to
the client. The server-side fetch of a client-controlled URL is a classic
**Server-Side Request Forgery (SSRF)** surface, and the download endpoint is an
**open-proxy** surface. Both are explicitly bounded in code. **FACT.**

## Controls in place

| Control | Where | Evidence |
| --- | --- | --- |
| SSRF guard — every resolved IP must be globally routable; a single private/loopback/link-local answer rejects the URL | `api/ssrf.py` (`ensure_public_url` / `SSRFError`) | **FACT** — rejects non-public addresses, unresolvable hosts, and mixed public/private DNS answers |
| Scheme allow-list (`http`/`https` only) | `api/ssrf.py`, `api/routers/explore.py` (download), `api/schemas.py` (`ExploreRequest.validate_url`) | **FACT** |
| Same-host traversal only | `api/crawler.py` (`_same_host`) | **FACT** (README/ARCHITECTURE) |
| Bounded crawl — max depth 5, max 500 nodes, `truncated` flag + per-request log | `api/constants.py`, `api/crawler.py` | **FACT** |
| Download size cap — 50 MB, aborts the stream when exceeded (logs a warning; the 200 has already begun so no 413 is possible mid-stream) | `api/routers/explore.py`, `MAX_DOWNLOAD_BYTES` in `api/constants.py` | **FACT** |
| Explicit HTTP timeouts on outbound requests | `api/constants.py`, httpx client | **FACT** (ARCHITECTURE) |
| CORS restricted to configured origins | `api/config.py`, `api/main.py` | **FACT** |
| No persistence — stateless, in-memory per request; no user data stored | whole backend | **FACT** — reduces data-at-rest exposure to nil |
| Secret scanning gate — `detect-secrets` baseline + pre-commit + CI (`secret-scan.yml`) | `.secrets.baseline`, `.pre-commit-config.yaml`, `.github/workflows/secret-scan.yml` | **FACT** |
| SAST in CI | `.github/workflows/sast.yml` | **FACT** |

## Secrets

- No secrets are committed. `.env.example` ships only empty/placeholder values
  (`SENTRY_DSN=` blank, `DEMO_MODE=false`). **FACT.**
- `.secrets.baseline` is an empty-results detect-secrets baseline (only plugin/filter
  config). **FACT.**
- Runtime secret: `SENTRY_DSN` is read from the environment, never hardcoded. **FACT.**

## Residual risks / notes for the owner

1. **SSRF TOCTOU (time-of-check/time-of-use).** `ensure_public_url` resolves the
   host and validates the IPs, but the subsequent httpx fetch resolves the host
   again; a hostile DNS server could return a public IP at check time and a private
   IP at fetch time (DNS rebinding). **INFERENCE — MEDIUM.** Not fixed here (docs-only
   task); owner should confirm whether httpx is pinned to the validated IP or whether
   this is accepted for a public-CDN-only tool.
2. **Redirect following.** Whether the crawler/download follows HTTP redirects, and
   whether a redirect target is re-validated against the SSRF guard, is not confirmed
   from the excerpts read. **UNKNOWN** — owner should verify redirects are either
   disabled or re-checked.
3. **Download size cap is post-response.** The cap aborts mid-stream rather than
   pre-checking `Content-Length`, so a client can still trigger up to ~50 MB of
   egress per request before abort. Bounded and by design. **FACT / accepted.**
4. **No auth / rate limiting on the endpoints** is visible in the excerpts read.
   For a public open-directory explorer this may be intentional, but an unauthenticated
   server-side fetcher can be used for amplification/scanning within the public-IP
   constraint. **INFERENCE — owner decision.** UNKNOWN whether a gateway/WAF fronts it
   in deployment.

No HIGH/CRITICAL finding is fixable in code within this docs-only task; items 1 and 2
are the ones to review first.
