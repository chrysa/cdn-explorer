# Roadmap — cdn-explorer

> Only items with evidence in the repository are listed. No speculative roadmap is
> invented. Tags: **FACT** / **INFERENCE** / **UNKNOWN**.

## Status

- Version indicators point to an early release: `RELEASE=cdn-explorer@0.1.0`
  (`.env.example`), and the `CHANGELOG.md` `[Unreleased]` section has no cut release
  yet. **FACT.**
- The tool is functional end-to-end (crawl + download + demo mode) with a passing-named
  backend and frontend test suite and an 85% coverage gate. **FACT.**

## Evidence-backed open items

| Item | Source | Note |
| --- | --- | --- |
| First tagged release / changelog cut | `CHANGELOG.md` (`[Unreleased]` only), `cliff.toml`, `make changelog` | No release has been cut yet. **FACT.** |
| Mutation-testing enforcement | `.github/workflows/mutation-testing.yml` | Workflow exists; whether it is a hard gate is **UNKNOWN**. |
| SSRF hardening review (DNS rebinding / redirect re-validation) | see `SECURITY.md` residual risks | Owner review recommended. **INFERENCE.** |

## Not planned (by design)

- No database / persistence — stateless is a deliberate constraint (`README.md`,
  `DECISIONS.md` D-0001, ARCHITECTURE). **FACT.**

No further roadmap could be substantiated from the repository. Items beyond this list
are **UNKNOWN**.
