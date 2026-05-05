"""Application-wide constants."""

from typing import Final

# HTTP
DEFAULT_TIMEOUT_SECONDS: Final[int] = 15
MAX_DEPTH: Final[int] = 5
MAX_NODES: Final[int] = 500
USER_AGENT: Final[str] = "cdn-explorer/1.0 (public resource crawler)"

# File extensions considered as downloadable assets
ASSET_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".mp4",
        ".mp3",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".txt",
        ".csv",
        ".json",
        ".xml",
    }
)

# Patterns that indicate an Apache / Nginx auto-generated directory listing
DIRECTORY_LISTING_MARKERS: Final[tuple[str, ...]] = (
    "Index of /",
    "Directory listing for",
    "<title>Index of",
)

# Download proxy — max file size allowed (50 MB)
MAX_DOWNLOAD_BYTES: Final[int] = 50 * 1024 * 1024
