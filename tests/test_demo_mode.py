"""Demo mode — the crawler serves fixtures and contacts no real CDN.

When ``settings.demo_mode`` is on, ``/api/explore`` returns the fixture tree and
``/api/download`` streams inline content, so no ``httpx`` request is ever made.
``/health`` reports the active flag for the frontend banner.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from api.config import settings


@pytest.fixture(autouse=True)
def _demo_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "demo_mode", True)


@pytest.mark.asyncio
async def test_health_reports_demo_mode(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["demo_mode"] is True


@pytest.mark.asyncio
async def test_explore_returns_fixtures_without_network(client: AsyncClient) -> None:
    # No httpx patching: in demo mode no request must be made at all.
    response = await client.post("/api/explore", json={"url": "https://anything.example/"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_nodes"] > 0
    assert data["truncated"] is False
    # Tree mirrors the live schema (dirs with children + files).
    names = {node["name"] for node in data["tree"]}
    assert "docs" in names
    assert any(node["is_dir"] and node["children"] for node in data["tree"])
    assert any("demo mode" in line for line in data["log"])


@pytest.mark.asyncio
async def test_download_returns_inline_demo_payload(client: AsyncClient) -> None:
    response = await client.get(
        "/api/download",
        params={"url": "https://cdn.demo.example/releases/logo.svg"},
    )
    assert response.status_code == 200
    assert b"Demo file: logo.svg" in response.content
    assert 'filename="logo.svg"' in response.headers["content-disposition"]
