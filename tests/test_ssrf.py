"""Unit tests for the SSRF guard."""

from __future__ import annotations

import pytest

from api.ssrf import SSRFError, validate_public_url


def _resolve_to(monkeypatch: pytest.MonkeyPatch, ip: str) -> None:
    def _fake_getaddrinfo(*_args: object, **_kwargs: object) -> list[object]:
        family = 10 if ":" in ip else 2
        return [(family, 1, 6, "", (ip, 0))]

    monkeypatch.setattr("api.ssrf.socket.getaddrinfo", _fake_getaddrinfo)


def test_public_url_is_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    _resolve_to(monkeypatch, "93.184.216.34")
    validate_public_url("https://cdn.example.com/file.pdf")


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",  # loopback
        "10.0.0.5",  # RFC 1918 private
        "192.168.1.10",  # RFC 1918 private
        "169.254.169.254",  # link-local / cloud metadata
        "::1",  # IPv6 loopback
    ],
)
def test_private_ip_is_blocked(monkeypatch: pytest.MonkeyPatch, ip: str) -> None:
    _resolve_to(monkeypatch, ip)
    with pytest.raises(SSRFError):
        validate_public_url(f"http://internal.example.com/{ip}")


def test_non_http_scheme_is_blocked() -> None:
    with pytest.raises(SSRFError):
        validate_public_url("ftp://cdn.example.com/file.pdf")


def test_unresolvable_host_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    import socket as _socket

    def _boom(*_args: object, **_kwargs: object) -> list[object]:
        raise _socket.gaierror("nope")

    monkeypatch.setattr("api.ssrf.socket.getaddrinfo", _boom)
    with pytest.raises(SSRFError):
        validate_public_url("http://does-not-resolve.example.com/")


def test_mixed_public_and_private_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_getaddrinfo(*_args: object, **_kwargs: object) -> list[object]:
        return [(2, 1, 6, "", ("93.184.216.34", 0)), (2, 1, 6, "", ("127.0.0.1", 0))]

    monkeypatch.setattr("api.ssrf.socket.getaddrinfo", _fake_getaddrinfo)
    with pytest.raises(SSRFError):
        validate_public_url("http://dns-rebind.example.com/")
