"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
