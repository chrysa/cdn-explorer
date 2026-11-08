# cdn-explorer — Design contract

> Product design contract for the CDN Explorer web UI (`app/`). Read it before any interface,
> component, style, navigation, interaction or asset work, and update it in the same change.
> This root file is the entry point; the visual identity and token roles live in
> [app/DESIGN.md](app/DESIGN.md) and are not copied here. The fleet rule, method and acceptance
> criteria live in shared-standards (`standards/rules/design.md`, `shared-standards/docs/DESIGN-CONTRACT.md`).
>
> Status of every statement: **[implemented]** links the code · **[decided]** cites the decision
> · **[proposed]** is not agreed yet.

## 1. Surface and status

- **Surface:** web app — a single-page React 19 / Vite UI with CSS modules, in front of the
  stateless FastAPI crawler in `api/`. **[implemented]** ([app/src/App.tsx](app/src/App.tsx))
- **Lifecycle:** prototype (shared-standards `repos.yml`: `status: dev`); a demo mode serves
  fixture data ([README.md](README.md)).
- **Detailed specs:** [app/DESIGN.md](app/DESIGN.md) — persona, token roles, ScanLog
  deviation. [app/design-system/cdn-explorer/MASTER.md](app/design-system/cdn-explorer/MASTER.md)
  is a generated design-system note (2026-08-05), not a decision.

## 2. Users, devices and priority tasks

| User | Context and device | Priority tasks |
| ---- | ------------------ | -------------- |
| Developer or archivist browsing a public open-directory listing | Desktop browser, occasional use; phone use possible | 1. paste a listing URL and see its file tree · 2. find a file in the tree · 3. download one file or a selection |

Primary action: **Explore** (submit the URL); after results, **Download N selected**.

## 3. Journeys and navigation

- **J1 — Explore a listing:** paste URL → Explore (button shows "Exploring…", disabled) →
  "N files found" + tree + collapsible scan log. Failure: an inline `role="alert"` message with
  the API detail; the URL stays in the field. **[implemented]**
  ([ExplorePage.tsx](app/src/pages/ExplorePage.tsx), [client.ts](app/src/api/client.ts))
- **J2 — Download:** expand folders → download one file through the proxy, or tick several and
  "Download N selected". **[implemented]** ([FileTree.tsx](app/src/components/FileTree.tsx))
- **J3 — Demo:** with `DEMO_MODE`, a persistent DEMO strip says fixture data is in use.
  **[implemented]** ([DemoBanner.tsx](app/src/components/DemoBanner.tsx))
- **Information architecture:** one page, no router: header → URL form → results (meta line,
  tree, scan log). A truncated crawl says "results truncated".
- **Density:** compact tree rows (16 px indent per level) — content is a file listing of up to
  500 nodes.

## 4. Identity

- **[decided]** chrysa "Console" persona with a magenta accent — rationale and roles in
  [app/DESIGN.md](app/DESIGN.md). Signature element: the magenta fill on the primary action and
  selection.
- **Drift:** [DECISIONS.md](DECISIONS.md) D-0002 still describes the earlier "Neon Brutalist"
  re-skin (radius 0, 2 px foreground borders, hard shadows); the code and `app/DESIGN.md`
  follow the Console persona (radius 4 px, hairline borders, soft shadows).

## 5. Tokens and components (owned elsewhere)

| Concern | Source of truth | Rules of use |
| ------- | --------------- | ------------ |
| Colour roles, themes, type, radius, shadow | [app/src/index.css](app/src/index.css) (`--color-*`, `--font-*`, `--radius`, `--shadow`) | light default, dark via `prefers-color-scheme`; roles in [app/DESIGN.md](app/DESIGN.md) |
| Spacing, breakpoints | per-module literals, one 480 px breakpoint in [ExplorePage.module.css](app/src/pages/ExplorePage.module.css) | no spacing tokens yet |
| Motion | literals (100–150 ms transitions) in the CSS modules | global reduced-motion block in `index.css` |
| Components | [app/src/components/](app/src/components/) | `FileTree`, `ScanLog`, `DemoBanner`; icons from `lucide-react` |

- **Shared contract:** `contract.css` not imported; `@chrysa/ui` not used.
- **Design debt:** CSS-module fallbacks carry old literal colours (`#0070f3`, `#888`, `#333`)
  that no longer match the tokens.

## 6. Interaction and states

- **Component states:** focus-visible 2 px accent outline globally; submit disabled while
  pending. **[implemented]**
- **Data states:**

  | State | Where it appears | Behaviour |
  | ----- | ---------------- | --------- |
  | Loading | Explore button | label "Exploring…", button disabled; no placeholder for the tree |
  | Empty | tree | "No files found at this URL." — no next action |
  | Error | below the form | API message in `role="alert"`; retry = submit again, input kept |
  | Offline / backend unreachable | — | same generic error; no banner |
  | Stale data | — | not applicable: each crawl is a fresh request |
  | Reconnect | — | not applicable |

- **Real-time:** none, except the demo-mode health poll (60 s).
- **Motion:** small hover transitions; no entrance effect for results (FE-053).

## 7. Responsive and support conventions

Single centred column; below 480 px the form stacks and the button becomes full width with a
44 px minimum height. **[implemented]** No other size tested.

## 8. Accessibility

- **Target:** WCAG 2.1 AA (canon floor).
- **Keyboard:** native form, buttons, checkboxes, links and `<details>`; visible focus.
- **Perception:** accent on fill uses `--color-accent-ink` for contrast; the scan log colours
  lines but the glyphs (✔ ✗ ⚠ →) also carry meaning. Contrast not measured in this pass.
- **Assistive technology:** labelled URL input, per-file "Select"/"Download" labels; folder
  toggles are labelled only "toggle" and expose no `aria-expanded`. No screen-reader pass.

## 9. Assets

| Asset | Source | Licence | Formats | Location |
| ----- | ------ | ------- | ------- | -------- |
| Inter, Space Grotesk, JetBrains Mono | hotlinked from Google Fonts in [index.css](app/src/index.css) | unknown in the repository (Google Fonts publishes these families under OFL-1.1; not recorded here) | WOFF2 via CDN | remote |
| Icons | `lucide-react` | ISC (package metadata) | inline SVG components | npm dependency |

No logo, favicon or image is shipped.

## 10. Acceptance criteria and evidence

- **Criteria:** the shared-standards observable list, applied to J1–J2: Explore is the dominant
  action; an error keeps the URL; a long or truncated listing stays usable; folder state is
  announced; reduced motion is honoured.
- **Existing tests:** Vitest + Testing Library —
  [ExplorePage.test.tsx](app/src/__tests__/ExplorePage.test.tsx) (input, results) and
  [DemoBanner.test.tsx](app/src/__tests__/DemoBanner.test.tsx). No browser or axe test.
- **Evidence log:**

  | Date | Change | Checks run | Result | Not run, and why |
  | ---- | ------ | ---------- | ------ | ---------------- |
  | 2026-11-08 | contract written from the code | source review of `app/src` | gaps listed in §11 | no browser run: documentation-only change |

## 11. Open choices, known gaps and maintenance

- **Known gaps (from the code, 2026-11-08):** fonts hotlinked from a third-party CDN instead of
  served locally; no placeholder while crawling; empty state offers no next action; folder
  toggle lacks a descriptive name and `aria-expanded`; no entrance motion (FE-053); stale
  literal fallbacks in CSS modules; D-0002 out of date (§4); no browser, axe or viewport test.
- **Open choices [proposed]:** vendor the three fonts as WOFF2 with their licence; record a
  decision superseding D-0002 with the Console persona.
- **Maintenance:** any UI change updates this file or [app/DESIGN.md](app/DESIGN.md) in the
  same PR.
