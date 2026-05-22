"""Tests for the /api/explore and /api/download endpoints."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from api.schemas import FileNode


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_explore_returns_tree(client: AsyncClient) -> None:
    mock_nodes = [
        FileNode(name="td-01.pdf", url="https://cdn.example.com/td-01.pdf", is_dir=False),
        FileNode(name="td-02.pdf", url="https://cdn.example.com/td-02.pdf", is_dir=False),
    ]

    with patch("api.routers.explore.crawl", new_callable=AsyncMock) as mock_crawl:
        mock_crawl.return_value = (mock_nodes, False, [])

        response = await client.post("/api/explore", json={"url": "https://cdn.example.com/docs/"})

    assert response.status_code == 200
    data = response.json()
    assert data["total_nodes"] == 2
    assert len(data["tree"]) == 2
    assert data["truncated"] is False
    assert data["log"] == []


@pytest.mark.asyncio
async def test_explore_invalid_url(client: AsyncClient) -> None:
    response = await client.post("/api/explore", json={"url": "ftp://cdn.example.com/"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_explore_missing_url(client: AsyncClient) -> None:
    response = await client.post("/api/explore", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_explore_truncated(client: AsyncClient) -> None:
    mock_nodes = [FileNode(name="f.pdf", url="https://cdn.example.com/f.pdf", is_dir=False)]
    with patch("api.routers.explore.crawl", new_callable=AsyncMock) as mock_crawl:
        mock_crawl.return_value = (mock_nodes, True, [])
        response = await client.post("/api/explore", json={"url": "https://cdn.example.com/"})
    assert response.status_code == 200
    assert response.json()["truncated"] is True


@pytest.mark.asyncio
async def test_explore_nested_tree(client: AsyncClient) -> None:
    child = FileNode(name="sub.pdf", url="https://cdn.example.com/sub/sub.pdf", is_dir=False)
    mock_nodes = [FileNode(name="sub", url="https://cdn.example.com/sub/", is_dir=True, children=[child])]
    with patch("api.routers.explore.crawl", new_callable=AsyncMock) as mock_crawl:
        mock_crawl.return_value = (mock_nodes, False, [])
        response = await client.post("/api/explore", json={"url": "https://cdn.example.com/"})
    assert response.status_code == 200
    assert response.json()["total_nodes"] == 2


# ── Download endpoint ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_download_invalid_scheme(client: AsyncClient) -> None:
    response = await client.get("/api/download", params={"url": "ftp://cdn.example.com/file.pdf"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_download_success(client: AsyncClient) -> None:
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/pdf", "content-length": "100"}
    mock_response.raise_for_status = MagicMock()

    async def _iter_bytes(chunk_size: int = 8192) -> AsyncGenerator[bytes]:
        yield b"pdf-content"

    mock_response.aiter_bytes = _iter_bytes

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.aclose = AsyncMock()

    with patch("api.routers.explore.httpx.AsyncClient", return_value=mock_client):
        response = await client.get("/api/download", params={"url": "https://cdn.example.com/file.pdf"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_download_upstream_error(client: AsyncClient) -> None:
    import httpx as _httpx

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_httpx.HTTPError("upstream down"))
    mock_client.aclose = AsyncMock()

    with patch("api.routers.explore.httpx.AsyncClient", return_value=mock_client):
        response = await client.get("/api/download", params={"url": "https://cdn.example.com/file.pdf"})

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_download_file_too_large(client: AsyncClient) -> None:
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/pdf", "content-length": str(100 * 1024 * 1024)}
    mock_response.raise_for_status = MagicMock()
    mock_response.aclose = AsyncMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()

    with patch("api.routers.explore.httpx.AsyncClient", return_value=mock_client):
        response = await client.get("/api/download", params={"url": "https://cdn.example.com/huge.iso"})

    assert response.status_code == 413
