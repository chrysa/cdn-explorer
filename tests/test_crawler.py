"""Unit tests for the crawler module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.crawler import _is_asset, _is_directory_listing, _normalize, _same_host, crawl

# ── helpers ───────────────────────────────────────────────────────────────────


def test_is_asset_pdf() -> None:
    assert _is_asset("https://cdn.example.com/file.pdf") is True


def test_is_asset_html_not_asset() -> None:
    assert _is_asset("https://cdn.example.com/index.html") is False


def test_is_directory_listing_true() -> None:
    html = "<html><title>Index of /docs</title></html>"
    assert _is_directory_listing(html) is True


def test_is_directory_listing_false() -> None:
    html = "<html><title>My School Portal</title></html>"
    assert _is_directory_listing(html) is False


def test_normalize_relative() -> None:
    assert _normalize("https://cdn.example.com/docs/", "td-01.pdf") == "https://cdn.example.com/docs/td-01.pdf"


def test_same_host_same() -> None:
    assert _same_host("https://cdn.example.com/", "https://cdn.example.com/file.pdf") is True


def test_same_host_different() -> None:
    assert _same_host("https://cdn.example.com/", "https://evil.com/file.pdf") is False


# ── crawl integration (mocked HTTP) ──────────────────────────────────────────

DIRECTORY_HTML = """
<html>
<title>Index of /docs</title>
<body>
<a href="../">Parent</a>
<a href="td-01.pdf">td-01.pdf</a>
<a href="td-02.pdf">td-02.pdf</a>
<a href="sub/">sub/</a>
</body>
</html>
"""

SUB_HTML = """
<html>
<title>Index of /docs/sub</title>
<body>
<a href="../">Parent</a>
<a href="exercise-03.pdf">exercise-03.pdf</a>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_crawl_directory_listing() -> None:
    responses: dict[str, str] = {
        "https://cdn.example.com/docs/": DIRECTORY_HTML,
        "https://cdn.example.com/docs/sub/": SUB_HTML,
    }

    def make_response(url: str) -> MagicMock:
        mock = MagicMock()
        mock.headers = {"content-type": "text/html"}
        mock.text = responses.get(str(url), "<html></html>")
        mock.raise_for_status = MagicMock()
        return mock

    with patch("api.crawler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        async def fake_get(url: str, **_: object) -> MagicMock:
            return make_response(url)

        mock_client.get = fake_get

        nodes, truncated = await crawl("https://cdn.example.com/docs/")

    assert not truncated
    assert any(n.name == "td-01.pdf" for n in nodes)
    assert any(n.name == "td-02.pdf" for n in nodes)
    dir_node = next((n for n in nodes if n.is_dir), None)
    assert dir_node is not None
    assert any(c.name == "exercise-03.pdf" for c in dir_node.children)
