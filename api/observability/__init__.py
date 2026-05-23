"""Observability — Sentry error tracking for cdn-explorer API."""

from __future__ import annotations

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

logger = logging.getLogger(__name__)

_SENTRY_DSN = os.getenv("SENTRY_DSN", "")
_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
_RELEASE = os.getenv("RELEASE", "cdn-explorer@0.1.0")


def init_sentry() -> None:
    """Initialise Sentry SDK.

    No-op when ``SENTRY_DSN`` is not set (development / CI without secrets).
    """
    if not _SENTRY_DSN:
        logger.debug("SENTRY_DSN not set — Sentry disabled")
        return

    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        environment=_ENVIRONMENT,
        release=_RELEASE,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
    logger.info("Sentry initialised (env=%s release=%s)", _ENVIRONMENT, _RELEASE)
