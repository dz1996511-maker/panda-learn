def parse_txt(content: bytes) -> str:
    """Parse plain text content from bytes."""
    return content.decode("utf-8", errors="replace")
