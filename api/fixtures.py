"""Demo-mode fixtures — realistic crawl results served without network access.

When ``settings.demo_mode`` is on, :func:`api.crawler.crawl` returns this fixed
tree instead of reaching a real CDN, so the app is fully explorable without any
external dependency. The shapes mirror exactly what a live crawl produces:
``(nodes, truncated, log)``.
"""

from __future__ import annotations

from api.schemas import FileNode

_DEMO_ROOT = "https://cdn.demo.example/releases/"


def _demo_tree() -> list[FileNode]:
    """Return a representative nested file tree (matches live crawl schema)."""
    return [
        FileNode(
            name="v1.2.0",
            url=f"{_DEMO_ROOT}v1.2.0/",
            is_dir=True,
            children=[
                FileNode(
                    name="cdn-explorer-1.2.0-linux-amd64.tar.gz",
                    url=f"{_DEMO_ROOT}v1.2.0/cdn-explorer-1.2.0-linux-amd64.tar.gz",
                    is_dir=False,
                    size="18.4 MB",
                ),
                FileNode(
                    name="cdn-explorer-1.2.0-darwin-arm64.tar.gz",
                    url=f"{_DEMO_ROOT}v1.2.0/cdn-explorer-1.2.0-darwin-arm64.tar.gz",
                    is_dir=False,
                    size="17.1 MB",
                ),
                FileNode(
                    name="SHA256SUMS",
                    url=f"{_DEMO_ROOT}v1.2.0/SHA256SUMS",
                    is_dir=False,
                    size="312 B",
                ),
            ],
        ),
        FileNode(
            name="docs",
            url=f"{_DEMO_ROOT}docs/",
            is_dir=True,
            children=[
                FileNode(
                    name="getting-started.pdf",
                    url=f"{_DEMO_ROOT}docs/getting-started.pdf",
                    is_dir=False,
                    size="1.3 MB",
                ),
                FileNode(
                    name="api-reference.pdf",
                    url=f"{_DEMO_ROOT}docs/api-reference.pdf",
                    is_dir=False,
                    size="842 KB",
                ),
            ],
        ),
        FileNode(
            name="logo.svg",
            url=f"{_DEMO_ROOT}logo.svg",
            is_dir=False,
            size="4 KB",
        ),
        FileNode(
            name="CHANGELOG.md",
            url=f"{_DEMO_ROOT}CHANGELOG.md",
            is_dir=False,
            size="9 KB",
        ),
    ]


def demo_crawl_result() -> tuple[list[FileNode], bool, list[str]]:
    """Return ``(nodes, truncated, log)`` mimicking a successful live crawl."""
    log = [
        f"→ {_DEMO_ROOT}",
        "  HTML page — is_listing=True",
        "  ✔ 2 dir(s), 2 file(s) found",
        "  (demo mode — fixture data, no network request made)",
    ]
    return _demo_tree(), False, log
