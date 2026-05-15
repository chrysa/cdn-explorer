"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.routers.explore import router as explore_router

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)

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


@app.get("/health", tags=["ops"], response_model=dict[str, str])
async def health() -> dict[str, str]:
    return {"status": "ok"}
