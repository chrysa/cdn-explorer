# cdn-explorer — Design

Visual identity for the CDN explorer UI. Implements the chrysa **Neon Brutalist**
design system (`shared-standards/docs/DESIGN-SYSTEM.md`).

## DNA

- **Radius 0** everywhere.
- **2px FG-colored borders** as structure on inputs, buttons, results, banners.
- **Hard offset shadows** (`--shadow: 4px 4px 0`, no blur). Buttons press into
  the shadow on hover.
- **Flat fills, no gradients/glow.**
- **Mono-forward:** JetBrains Mono (UI/data) + Space Grotesk (display headings).
- **One acid accent:** **magenta** — `#ff4dff` (dark), `#c800c8` (light) — used as
  a block with `--color-accent-ink` on top (WCAG AA), never thin acid text.

## Tokens

Single source of truth: `src/index.css`, `--color-*` custom properties, with the
dark scheme via `@media (prefers-color-scheme: dark)` (canonical). Every
`*.module.css` consumes these vars, so the re-skin propagates without
per-component rewrites.

| role | dark | light |
|---|---|---|
| `--color-bg` | `#0e0e10` | `#fafafa` |
| `--color-surface` | `#18181b` | `#ffffff` |
| `--color-border` (loud) | `#fafafa` | `#0e0e10` |
| `--color-accent` (magenta) | `#ff4dff` | `#c800c8` |
| `--color-accent-ink` | `#0e0e10` | `#ffffff` |

## Deviation

The `ScanLog` crawl log keeps a terminal-style fixed syntax palette (sky/green/
red/amber line classes) for legibility. Recorded as **D-0002** in `DECISIONS.md`.

## Constraints kept

- No framework migration (plain CSS + CSS modules retained).
- All `data-testid` selectors and the dark `prefers-color-scheme` switch
  preserved — no component logic or test changed.
- `prefers-reduced-motion` respected.
