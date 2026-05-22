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
        # Documents
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".csv",
        ".md",
        # Archives
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".bz2",
        ".xz",
        # Media
        ".mp4",
        ".webm",
        ".ogg",
        ".mp3",
        ".wav",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".bmp",
        ".ico",
        ".svg",
        # Web assets
        ".js",
        ".mjs",
        ".cjs",
        ".css",
        ".html",
        ".htm",
        ".ts",
        ".jsx",
        ".tsx",
        ".map",
        # Fonts
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        # Data
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        # Disk images & installers
        ".iso",
        ".img",
        ".dmg",
        ".bin",
        ".exe",
        ".msi",
        ".deb",
        ".rpm",
        ".apk",
        ".wsl",
        # EFI / firmware
        ".efi",
        # Checksums & signatures
        ".sig",
        ".asc",
        ".sha256",
        ".sha512",
        # Misc
        ".torrent",
        ".zsync",
        ".list",
        ".manifest",
        ".cfg",
        ".conf",
        ".pub",
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
