"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.main import app

# A public, globally-routable address the SSRF guard accepts (example.com's IP).
_PUBLIC_IP = "93.184.216.34"


@pytest.fixture(autouse=True)
def _public_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolve every host to a public IP so the SSRF guard passes under mocked HTTP.

    Tests mock the HTTP transport but not DNS; without this the guard's real
    ``getaddrinfo`` call would fail for fixture hosts. SSRF-specific tests patch
    ``getaddrinfo`` themselves and override this.
    """

    def _fake_getaddrinfo(*_args: object, **_kwargs: object) -> list[object]:
        return [(2, 1, 6, "", (_PUBLIC_IP, 0))]

    monkeypatch.setattr("api.ssrf.socket.getaddrinfo", _fake_getaddrinfo)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
