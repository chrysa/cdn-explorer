---
name: frontend-e2e-smoke
description: "Browser-level smoke test for the React frontend, driven through the Playwright MCP server against the dev stack. Not for unit/component tests (Vitest already covers those) — this is the one check that exercises a real browser end to end."
disable-model-invocation: true
---

# Frontend E2E Smoke

Drives the Playwright MCP server against the running dev stack to confirm the
core user flow works in a real browser. User-invoked only: it starts a
long-running dev server as a side effect, so it must never fire automatically.

## Preflight

Confirm the Playwright MCP server is available (`.mcp.json` → `playwright`).
If it isn't connected, stop and tell the user to check their MCP config
instead of proceeding.

## Steps

1. Start the dev stack: `make up-dev` (backend on `:8010`, frontend on
   `:5173`). Wait until `http://localhost:5173` responds.
2. Using the Playwright MCP tools, navigate to `http://localhost:5173`.
3. Drive the core flow:
   - Enter a CDN URL in the input field.
   - Confirm the resulting tree/listing renders.
   - Trigger the download proxy on one entry.
   - Confirm a successful response (no error toast/state).
4. Report pass/fail per step. On failure, capture a screenshot via the
   Playwright MCP server and include it in the report.
5. Stop the dev stack (`make down`) when done, even on failure.

## Out of scope

- Component/unit-level checks — those stay in Vitest (`app/`).
- Cross-browser matrix — single default browser only, this is a smoke test,
  not a compatibility suite.
