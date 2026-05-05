"""Tests for the /api/explore endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

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
        mock_crawl.return_value = (mock_nodes, False)

        response = await client.post("/api/explore", json={"url": "https://cdn.example.com/docs/"})

    assert response.status_code == 200
    data = response.json()
    assert data["total_nodes"] == 2
    assert len(data["tree"]) == 2
    assert data["truncated"] is False


@pytest.mark.asyncio
async def test_explore_invalid_url(client: AsyncClient) -> None:
    response = await client.post("/api/explore", json={"url": "ftp://cdn.example.com/"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_explore_missing_url(client: AsyncClient) -> None:
    response = await client.post("/api/explore", json={})
    assert response.status_code == 422
