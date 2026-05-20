"""Unit tests for the crawler module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.crawler import _is_asset, _is_directory_listing, _normalize, _same_host, _try_parse_nginx_json, crawl

# ── helpers ───────────────────────────────────────────────────────────────────


def test_is_asset_pdf() -> None:
    assert _is_asset("https://cdn.example.com/file.pdf") is True


def test_is_asset_html_is_asset() -> None:
    assert _is_asset("https://cdn.example.com/index.html") is True


def test_is_asset_php_not_asset() -> None:
    assert _is_asset("https://cdn.example.com/page.php") is False


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

        nodes, truncated, log = await crawl("https://cdn.example.com/docs/")

    assert not truncated
    assert any(n.name == "td-01.pdf" for n in nodes)
    assert any(n.name == "td-02.pdf" for n in nodes)
    dir_node = next((n for n in nodes if n.is_dir), None)
    assert dir_node is not None
    assert any(c.name == "exercise-03.pdf" for c in dir_node.children)
    assert any("https://cdn.example.com/docs/" in entry for entry in log)


NON_LISTING_HTML = """
<html>
<title>CDN Assets</title>
<body>
<a href="styles/">styles/</a>
<a href="app.js">app.js</a>
</body>
</html>
"""

STYLES_HTML = """
<html>
<title>CDN Assets — styles</title>
<body>
<a href="main.css">main.css</a>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_crawl_non_listing_follows_subdirs() -> None:
    """Subdirectories ending with '/' are followed even without a directory listing marker."""
    responses: dict[str, str] = {
        "https://cdn.example.com/assets/": NON_LISTING_HTML,
        "https://cdn.example.com/assets/styles/": STYLES_HTML,
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

        nodes, truncated, log = await crawl("https://cdn.example.com/assets/")

    assert not truncated
    assert any(n.name == "app.js" for n in nodes)
    dir_node = next((n for n in nodes if n.is_dir), None)
    assert dir_node is not None
    assert dir_node.name == "styles"
    assert any(c.name == "main.css" for c in dir_node.children)
    assert len(log) > 0


@pytest.mark.asyncio
async def test_crawl_truncated_still_returns_nodes() -> None:
    """When MAX_NODES is hit, already-found nodes must still be returned."""
    from unittest.mock import patch as _patch

    big_dir_html = "<html><title>Index of /</title><body>"
    for i in range(10):
        big_dir_html += f'<a href="dir{i}/">dir{i}/</a>'
    big_dir_html += "</body></html>"

    def make_response(url: str) -> MagicMock:
        mock = MagicMock()
        mock.headers = {"content-type": "text/html"}
        mock.text = big_dir_html
        mock.raise_for_status = MagicMock()
        return mock

    with patch("api.crawler.httpx.AsyncClient") as mock_client_cls, _patch("api.crawler.MAX_NODES", 3):
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get = AsyncMock(side_effect=lambda url, **_: make_response(url))

        nodes, truncated, log = await crawl("https://cdn.example.com/")

    assert truncated is True
    assert len(nodes) > 0, "Nodes found before truncation must be returned"
    assert any("MAX_NODES" in entry or "truncat" in entry.lower() for entry in log)


# ── nginx JSON autoindex ──────────────────────────────────────────────────────

NGINX_JSON = """
[
  {"name":"fonts/","type":"directory","mtime":"Thu, 01 Jan 2015 00:00:00 GMT"},
  {"name":"app.js","type":"file","mtime":"Thu, 01 Jan 2015 00:00:00 GMT","size":1234},
  {"name":"style.css","type":"file","mtime":"Thu, 01 Jan 2015 00:00:00 GMT","size":567}
]
"""

NGINX_JSON_SUBDIR = """
[
  {"name":"roboto.woff2","type":"file","mtime":"Thu, 01 Jan 2015 00:00:00 GMT","size":89}
]
"""


def test_try_parse_nginx_json_valid() -> None:
    entries = _try_parse_nginx_json(NGINX_JSON)
    assert entries is not None
    assert len(entries) == 3
    assert entries[0]["name"] == "fonts/"
    assert entries[0]["type"] == "directory"


def test_try_parse_nginx_json_not_json() -> None:
    assert _try_parse_nginx_json("<html>not json</html>") is None


def test_try_parse_nginx_json_wrong_shape() -> None:
    # Valid JSON but not nginx autoindex format
    assert _try_parse_nginx_json('{"key": "value"}') is None
    assert _try_parse_nginx_json("[1, 2, 3]") is None


@pytest.mark.asyncio
async def test_crawl_nginx_json_listing() -> None:
    """Crawler must parse nginx JSON autoindex (application/json) responses."""
    responses: dict[str, tuple[str, str]] = {
        "https://cdn.example.com/": (NGINX_JSON, "application/json"),
        "https://cdn.example.com/fonts/": (NGINX_JSON_SUBDIR, "application/json"),
    }

    def make_response(url: str) -> MagicMock:
        body, ct = responses.get(url, ("{}", "application/json"))
        mock = MagicMock()
        mock.headers = {"content-type": ct}
        mock.text = body
        mock.raise_for_status = MagicMock()
        return mock

    with patch("api.crawler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        async def fake_get(url: str, **_: object) -> MagicMock:
            return make_response(url)

        mock_client.get = fake_get

        nodes, truncated, log = await crawl("https://cdn.example.com/")

    assert not truncated
    assert any(n.name == "app.js" for n in nodes)
    assert any(n.name == "style.css" for n in nodes)
    fonts_node = next((n for n in nodes if n.is_dir), None)
    assert fonts_node is not None
    assert fonts_node.name == "fonts"
    assert any(c.name == "roboto.woff2" for c in fonts_node.children)
    assert any("JSON listing" in entry for entry in log)
