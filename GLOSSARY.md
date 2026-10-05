# Glossary — cdn-explorer

> Terms as used in this repository. **FACT** unless tagged otherwise.

| Term | Meaning |
| --- | --- |
| **Directory listing / autoindex** | An HTML or JSON index page a web server (nginx/Apache) auto-generates for a directory with no index file. The crawler detects these to enumerate files. |
| **nginx JSON autoindex** | nginx's `autoindex_format json` output; parsed by `_try_parse_nginx_json` in `api/crawler.py`. |
| **Asset** | A file whose extension is in the known-downloadable allow-list (`api/constants.py`); non-assets (e.g. `.php`) are excluded from the tree. |
| **Node / FileNode** | An entry in the file tree: `name`, `url`, `is_dir`, optional `size`, `children` (`api/schemas.py`). |
| **Crawl bounds** | The traversal limits: same-host only, max depth 5, max 500 nodes (`api/constants.py`). |
| **`truncated`** | Boolean flag on the explore response set when a crawl bound stopped enumeration early. |
| **`log`** | Per-request list of human-readable crawl steps returned by `/api/explore` and shown in the UI `ScanLog`. |
| **Download proxy** | The `/api/download` endpoint that streams a chosen public file back through the backend, scheme-checked and size-capped (50 MB). |
| **SSRF guard** | `api/ssrf.py` — rejects URLs that resolve to any non-public IP; defends the server-side fetch (`SSRFError`). |
| **Demo mode** | `DEMO_MODE=true` — serves fixture data (`api/fixtures.py`), never contacts a real CDN, and shows a DEMO banner. Never enabled in prod. |
| **Neon Brutalist** | The chrysa ecosystem design system the UI adopts (magenta accent `#ff4dff`, radius 0, 2px borders, hard shadows); see `DECISIONS.md` D-0002. |
| **Canon / shared-standards** | The chrysa portfolio standards this repo follows (`standards/STANDARDS.chrysa.md`); the canon wins over any local annexe. |
| **Context files** | Generated agent-context files (`handover.md`, `ai-instructions.md`, `context-map.json`, `llms-full.txt`) produced by `scripts/gen_context_files.py` (ADR D-0012) — do not hand-edit. |
| **GitNexus** | Code-intelligence index used by Claude tooling for this repo (see CLAUDE.md gitnexus block). |
