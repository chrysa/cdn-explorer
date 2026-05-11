"""CDN crawler — parses directory listings and extracts asset links."""

from __future__ import annotations

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


def _is_asset(href: str) -> bool:
    path = urlparse(href).path.lower()
    return any(path.endswith(ext) for ext in ASSET_EXTENSIONS)


def _same_host(base_url: str, href: str) -> bool:
    base = urlparse(base_url)
    target = urlparse(href)
    return target.netloc == "" or target.netloc == base.netloc


def _normalize(base_url: str, href: str) -> str:
    return urljoin(base_url, href)


async def crawl(root_url: str) -> tuple[list[FileNode], bool]:
    """
    Crawl *root_url* and return (nodes, truncated).

    Strategy:
    - If the page is a directory listing, recurse into subdirectories.
    - Otherwise, extract all asset-extension hrefs from the page.
    """
    nodes: list[FileNode] = []
    seen: set[str] = set()
    truncated = False

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
        )

    return nodes, truncated


async def _crawl_url(
    *,
    client: httpx.AsyncClient,
    url: str,
    nodes: list[FileNode],
    seen: set[str],
    depth: int,
) -> bool:
    """Recursively crawl *url* and populate *nodes*. Returns True if truncated."""
    if depth > MAX_DEPTH or len(seen) >= MAX_NODES:
        return True

    if url in seen:
        return False
    seen.add(url)

    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("HTTP error fetching %s: %s", url, exc)
        return False

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        # It's a direct file — add it as a leaf node
        name = url.rstrip("/").split("/")[-1] or url
        nodes.append(FileNode(name=name, url=url, is_dir=False))
        return False

    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    is_listing = _is_directory_listing(html)

    dir_nodes: list[FileNode] = []
    file_nodes: list[FileNode] = []

    for anchor in soup.find_all("a", href=True):
        raw_href = anchor.get("href", "")
        href: str = str(raw_href)

        # Skip parent directory links and anchors
        if href in ("#", "/", "../", "./") or href.startswith("?") or href.startswith("mailto:"):
            continue

        full_url = _normalize(url, href)

        if not _same_host(url, full_url):
            continue

        if full_url in seen:
            continue

        if len(seen) >= MAX_NODES:
            return True

        name = href.rstrip("/").split("/")[-1] or href
        is_dir = href.endswith("/") and is_listing

        if is_dir:
            child_nodes: list[FileNode] = []
            truncated = await _crawl_url(
                client=client,
                url=full_url,
                nodes=child_nodes,
                seen=seen,
                depth=depth + 1,
            )
            dir_nodes.append(FileNode(name=name, url=full_url, is_dir=True, children=child_nodes))
            if truncated:
                return True
        elif _is_asset(full_url):
            seen.add(full_url)
            file_nodes.append(FileNode(name=name, url=full_url, is_dir=False))

    nodes.extend(dir_nodes)
    nodes.extend(file_nodes)
    return False
