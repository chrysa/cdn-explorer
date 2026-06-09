# DECISIONS — cdn-explorer

> Repository-local ADRs (Architectural Decision Records). Numbering: D-XXXX.
> Any deviation from [CODE_MANIFEST.md](../../shared-standards/CODE_MANIFEST.md) must be documented here.
> No active deviation → this project follows all chrysa global standards.

---

## D-0001 — Adherence to chrysa global standards

**Date**: 2026-05-25
**Status**: accepted

This project follows all conventions defined in `CODE_MANIFEST.md` (chrysa portfolio standards).
No active deviation is in effect. Any future deviation must be added as a new ADR entry below.

---

## D-0002 — Frontend visual identity: chrysa "Neon Brutalist" (magenta)

**Date**: 2026-06-10
**Status**: accepted

The explorer UI adopts the ecosystem Neon Brutalist design system
(`shared-standards/docs/DESIGN-SYSTEM.md`): radius 0, 2px FG-colored borders,
hard offset shadows (`4px 4px 0`, no blur), flat fills, mono-forward (JetBrains
Mono + Space Grotesk display), one acid accent — **magenta `#ff4dff`**.

The re-skin is driven through the `--color-*` token layer in `app/src/index.css`
(token values + base styling); the token names and the `prefers-color-scheme`
dark switch are preserved, so every `*.module.css` inherits. A few modules that
hardcoded radius/hex (ExplorePage form/results, banners, file tree) were
migrated onto the same tokens. No component logic, route, or `data-testid`
changed.

**Documented deviation.** The `ScanLog` crawl log keeps its terminal-style fixed
syntax colors (sky/green/red/amber line classes) for log legibility; structural
surfaces carry the loud 2px FG border.

---
