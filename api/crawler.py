"""CDN crawler — parses directory listings and extracts asset links."""

from __future__ import annotations

import json
import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from api.constants import (
    ASSET_EXTENSIONS,
    DEFAULT_TIMEOUT_SECONDS,
    DIRECTORY_LISTING_MARKERS,
    MAX_DEPTH,
    MAX_NODES,
    USER_AGENT,
)
from api.schemas import FileNode

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": USER_AGENT}


def _is_directory_listing(html: str) -> bool:
    return any(marker in html for marker in DIRECTORY_LISTING_MARKERS)


def _try_parse_nginx_json(text: str) -> list[dict[str, str]] | None:
    """Try to parse a nginx autoindex JSON response.

    Nginx with ``autoindex_format json`` returns a JSON array of objects with
    ``name``, ``type`` (``"file"`` or ``"directory"``), ``mtime``, and optional
    ``size`` fields.  Returns ``None`` when *text* is not in that format.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError, ValueError:
        return None
    if not isinstance(data, list):
        return None
    # Validate that at least the first entry looks like an nginx autoindex entry
    if data and not isinstance(data[0], dict):
        return None
    if data and "name" not in data[0]:
        return None
    return [{str(k): str(v) for k, v in entry.items()} for entry in data]


def _is_asset(href: str) -> bool:
    path = urlparse(href).path.lower()
    return any(path.endswith(ext) for ext in ASSET_EXTENSIONS)


def _same_host(base_url: str, href: str) -> bool:
    base = urlparse(base_url)
    target = urlparse(href)
    return target.netloc == "" or target.netloc == base.netloc


def _normalize(base_url: str, href: str) -> str:
    return urljoin(base_url, href)


async def crawl(root_url: str) -> tuple[list[FileNode], bool, list[str]]:
    """
    Crawl *root_url* and return (nodes, truncated, log).

    Strategy:
    - If the page is a directory listing, recurse into subdirectories.
    - Otherwise, extract all asset-extension hrefs from the page.
    """
    nodes: list[FileNode] = []
    seen: set[str] = set()
    log: list[str] = []

    async with httpx.AsyncClient(
        headers=_HEADERS,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        follow_redirects=True,
    ) as client:
        truncated = await _crawl_url(
            client=client,
            url=root_url,
            nodes=nodes,
            seen=seen,
            depth=0,
            log=log,
        )

    return nodes, truncated, log


async def _crawl_url(
    *,
    client: httpx.AsyncClient,
    url: str,
    nodes: list[FileNode],
    seen: set[str],
    depth: int,
    log: list[str],
) -> bool:
    """Recursively crawl *url* and populate *nodes*. Returns True if truncated."""
    if depth > MAX_DEPTH or len(seen) >= MAX_NODES:
        log.append(f"⚠ Limit reached — stopping at {url}")
        return True

    if url in seen:
        return False
    seen.add(url)

    indent = "  " * depth
    log.append(f"{indent}→ {url}")

    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        log.append(f"{indent}  ✗ {type(exc).__name__}: {exc}")
        logger.warning("HTTP error fetching %s: %s", url, exc)
        return False

    content_type = response.headers.get("content-type", "")

    # ── nginx JSON autoindex ────────────────────────────────────────────────
    # Nginx with `autoindex_format json;` returns application/json (or sometimes
    # text/plain) with an array [{name, type, mtime, size?}, ...].
    if "text/html" not in content_type:
        json_entries = _try_parse_nginx_json(response.text)
        if json_entries is not None:
            log.append(f"{indent}  JSON listing — {len(json_entries)} entries")
            dir_nodes: list[FileNode] = []
            file_nodes: list[FileNode] = []
            for entry in json_entries:
                name: str = entry.get("name", "")
                if not name:
                    continue
                full_url = _normalize(url, name)
                if full_url in seen:
                    continue
                if len(seen) >= MAX_NODES:
                    log.append(f"{indent}  ⚠ MAX_NODES ({MAX_NODES}) reached — truncating")
                    nodes.extend(dir_nodes)
                    nodes.extend(file_nodes)
                    return True
                entry_type: str = entry.get("type", "file")
                if entry_type == "directory":
                    child_nodes: list[FileNode] = []
                    truncated = await _crawl_url(
                        client=client,
                        url=full_url.rstrip("/") + "/",
                        nodes=child_nodes,
                        seen=seen,
                        depth=depth + 1,
                        log=log,
                    )
                    dir_nodes.append(FileNode(name=name.rstrip("/"), url=full_url, is_dir=True, children=child_nodes))
                    if truncated:
                        nodes.extend(dir_nodes)
                        nodes.extend(file_nodes)
                        return True
                elif _is_asset(full_url):
                    seen.add(full_url)
                    file_nodes.append(FileNode(name=name, url=full_url, is_dir=False))
            log.append(f"{indent}  ✔ {len(dir_nodes)} dir(s), {len(file_nodes)} file(s) found")
            nodes.extend(dir_nodes)
            nodes.extend(file_nodes)
            return False

        # Not JSON listing — treat as a direct file asset
        name = url.rstrip("/").split("/")[-1] or url
        log.append(f"{indent}  📄 {name} [{content_type}]")
        nodes.append(FileNode(name=name, url=url, is_dir=False))
        return False

    # ── HTML directory listing ──────────────────────────────────────────────
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    is_listing = _is_directory_listing(html)
    log.append(f"{indent}  HTML page — is_listing={is_listing}")

    dir_nodes = []
    file_nodes = []
    skipped_offhost = 0

    for anchor in soup.find_all("a", href=True):
        raw_href = anchor.get("href", "")
        href: str = str(raw_href)

        # Skip parent directory links, anchors, and query-only links
        if href in ("/", "../", "./") or href.startswith("#") or href.startswith("?") or href.startswith("mailto:"):
            continue

        full_url = _normalize(url, href)

        if not _same_host(url, full_url):
            skipped_offhost += 1
            continue

        if full_url in seen:
            continue

        if len(seen) >= MAX_NODES:
            log.append(f"{indent}  ⚠ MAX_NODES ({MAX_NODES}) reached — truncating")
            nodes.extend(dir_nodes)
            nodes.extend(file_nodes)
            return True

        name = href.rstrip("/").split("/")[-1] or href
        is_dir = href.endswith("/")

        if is_dir:
            child_nodes = []
            truncated = await _crawl_url(
                client=client,
                url=full_url,
                nodes=child_nodes,
                seen=seen,
                depth=depth + 1,
                log=log,
            )
            dir_nodes.append(FileNode(name=name, url=full_url, is_dir=True, children=child_nodes))
            if truncated:
                nodes.extend(dir_nodes)
                nodes.extend(file_nodes)
                return True
        elif _is_asset(full_url):
            seen.add(full_url)
            file_nodes.append(FileNode(name=name, url=full_url, is_dir=False))

    if skipped_offhost:
        log.append(f"{indent}  ↷ {skipped_offhost} off-host link(s) skipped")
    log.append(f"{indent}  ✔ {len(dir_nodes)} dir(s), {len(file_nodes)} file(s) found")
    nodes.extend(dir_nodes)
    nodes.extend(file_nodes)
    return False
