"""Explore router — CDN crawling and file download proxy."""

from __future__ import annotations

import logging
import urllib.parse
from collections.abc import AsyncGenerator, Generator
from typing import Annotated

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from api.config import settings
from api.constants import DEFAULT_TIMEOUT_SECONDS, MAX_DOWNLOAD_BYTES, USER_AGENT
from api.crawler import crawl
from api.schemas import ExploreRequest, ExploreResponse, FileNode
from api.ssrf import SSRFError, validate_public_url

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["explore"])

_HEADERS = {"User-Agent": USER_AGENT}


@router.post(
    "/explore",
    response_model=ExploreResponse,
    summary="Crawl a CDN URL and return its file tree",
)
async def explore(body: ExploreRequest) -> ExploreResponse:
    nodes, truncated, log = await crawl(body.url)
    return ExploreResponse(
        root_url=body.url,
        total_nodes=sum(1 for _ in _flatten(nodes)),
        tree=nodes,
        truncated=truncated,
        log=log,
    )


@router.get(
    "/download",
    response_model=None,
    summary="Proxy-download a public file from a CDN URL",
)
async def download(
    url: Annotated[str, Query(description="Public file URL to download")],
) -> StreamingResponse:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs are supported")

    # Demo mode — serve a small inline payload without contacting any real CDN,
    # so fixture file links remain downloadable while exploring.
    if settings.demo_mode:
        filename = url.rstrip("/").split("/")[-1] or "download"
        body = f"Demo file: {filename}\nThis is fixture content served in demo mode.\n".encode()

        async def _demo_stream() -> AsyncGenerator[bytes]:
            yield body

        return StreamingResponse(
            _demo_stream(),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    try:
        validate_public_url(url)
    except SSRFError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    client = httpx.AsyncClient(headers=_HEADERS, timeout=DEFAULT_TIMEOUT_SECONDS, follow_redirects=True)
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc

    content_length = response.headers.get("content-length")
    if content_length and int(content_length) > MAX_DOWNLOAD_BYTES:
        await client.aclose()
        raise HTTPException(status_code=413, detail="File exceeds maximum allowed size (50 MB)")

    filename = url.rstrip("/").split("/")[-1] or "download"
    content_type = response.headers.get("content-type", "application/octet-stream")

    async def _stream() -> AsyncGenerator[bytes]:
        total = 0
        try:
            async for chunk in response.aiter_bytes(chunk_size=8192):
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    # The 200 response has already begun, so no 413 can be sent
                    # now. Raise instead of returning silently so the client
                    # sees an aborted transfer rather than a truncated file that
                    # looks complete.
                    logger.warning("Download exceeded %d bytes, aborting stream: %s", MAX_DOWNLOAD_BYTES, url)
                    raise RuntimeError("File exceeds maximum allowed size (50 MB)")
                yield chunk
        finally:
            await client.aclose()

    return StreamingResponse(
        _stream(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _flatten(nodes: list[FileNode]) -> Generator[FileNode]:
    for node in nodes:
        yield node
        if node.children:
            yield from _flatten(node.children)
