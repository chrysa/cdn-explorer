# cdn-explorer — Design

Visual identity for the CDN explorer UI. Implements the chrysa design system,
**Console persona** (`shared-standards/docs/DESIGN-SYSTEM.md` §1 + [ADR 0002](https://github.com/chrysa/shared-standards/blob/main/docs/adr/0002-design-personas.md)).
cdn-explorer is a dense, data-forward dev tool — the Console genre.

## Persona

- **Subtle rounding** — `--radius: 4px`.
- **1px hairline borders** — `--color-border` `#2e2e33` dark / `#d4d4d8` light
  (not foreground-loud), structure carried by depth, not heavy outlines.
- **Soft restrained shadows** — `--shadow: 0 1px 3px …` (no hard offset).
- **Readable sans body** — Inter (`--font-sans`) in normal case; **mono reserved
  for data** (JetBrains Mono); Space Grotesk for display headings.
- **One accent:** **magenta** — `#ff4dff` (dark), `#c800c8` (light) — used as a
  fill block with `--color-accent-ink` on top (WCAG AA), never thin acid text.

## Tokens

Single source of truth: `src/index.css`, `--color-*` custom properties, with the
dark scheme via `@media (prefers-color-scheme: dark)` (canonical). Every
`*.module.css` consumes these vars, so the persona migration propagates without
per-component rewrites (token revalue + a hairline/radius literal sweep).

| role | dark | light |
|---|---|---|
| `--color-bg` | `#0e0e10` | `#fafafa` |
| `--color-surface` | `#18181b` | `#ffffff` |
| `--color-border` (hairline) | `#2e2e33` | `#d4d4d8` |
| `--color-accent` (magenta) | `#ff4dff` | `#c800c8` |
| `--color-accent-ink` | `#0e0e10` | `#ffffff` |

## Deviation

The `ScanLog` crawl log keeps a terminal-style fixed syntax palette (sky/green/
red/amber line classes) for legibility. Recorded as **D-0002** in `DECISIONS.md`.

## Constraints kept

- No framework migration (plain CSS + CSS modules retained).
- All `data-testid` selectors and the dark `prefers-color-scheme` switch
  preserved — no component logic or test changed.
- `prefers-reduced-motion` respected; focus outline kept at 2px in the accent.
