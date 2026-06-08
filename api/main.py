"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.observability import init_sentry
from api.routers.explore import router as explore_router

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)

init_sentry()

app = FastAPI(
    title="CDN Explorer",
    description="Explore and download files from public CDN directory listings.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(explore_router)


@app.get("/health", tags=["ops"], response_model=dict[str, object])
async def health() -> dict[str, object]:
    """Liveness probe that also reports whether demo mode is active.

    When ``demo_mode`` is true, every crawl returns fixture data and no real
    CDN is contacted; the frontend shows a persistent "DEMO" banner.
    """
    return {"status": "ok", "demo_mode": settings.demo_mode}
