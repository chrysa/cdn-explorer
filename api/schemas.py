"""Pydantic schemas for the CDN explorer API."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class ExploreRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            msg = "URL must start with http:// or https://"
            raise ValueError(msg)
        return v.rstrip("/")


class FileNode(BaseModel):
    name: str
    url: str
    is_dir: bool
    size: str | None = None
    children: list[FileNode] = []


class ExploreResponse(BaseModel):
    root_url: str
    total_nodes: int
    tree: list[FileNode]
    truncated: bool = False
    log: list[str] = []


class DownloadInfo(BaseModel):
    filename: str
    content_type: str
    size: int | None
