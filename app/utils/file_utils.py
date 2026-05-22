from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".txt": "txt",
    ".md": "md",
    ".markdown": "md",
    ".html": "html",
    ".htm": "html",
    ".pdf": "pdf",
}


def detect_file_type(filename: str) -> str | None:
    """Detect the file type from its extension."""
    ext = Path(filename).suffix.lower()
    return SUPPORTED_EXTENSIONS.get(ext)


def is_supported_file(filename: str) -> bool:
    """Check if a file type is supported for import."""
    return detect_file_type(filename) is not None
