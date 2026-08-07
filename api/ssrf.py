"""SSRF guard — reject URLs that resolve to non-public IP ranges.

The service fetches arbitrary user-supplied URLs (crawler + download proxy).
Without validation an attacker could point it at internal resources such as
``127.0.0.1``, RFC 1918 ranges (``10.x``, ``192.168.x``), or the cloud metadata
endpoint (``169.254.169.254``) and exfiltrate their contents. This module
resolves the target host and blocks any address that is not globally routable.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class SSRFError(ValueError):
    """Raised when a URL targets a disallowed (non-public) address."""


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def validate_public_url(url: str) -> None:
    """Raise :class:`SSRFError` unless *url* resolves only to public IPs.

    Every address the hostname resolves to must be globally routable; a single
    private/loopback/link-local answer rejects the whole URL (defends against
    DNS entries that mix public and internal addresses).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SSRFError("Only http/https URLs are supported")

    host = parsed.hostname
    if not host:
        raise SSRFError("URL has no host")

    try:
        infos = socket.getaddrinfo(host, parsed.port or None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(f"Cannot resolve host: {host}") from exc

    if not infos:
        raise SSRFError(f"Cannot resolve host: {host}")

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if _is_blocked_ip(ip):
            raise SSRFError(f"URL resolves to a non-public address: {ip}")
