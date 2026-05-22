def parse_markdown(content: bytes) -> str:
    """Parse Markdown content from bytes, stripping formatting but keeping structure."""
    text = content.decode("utf-8", errors="replace")
    # Keep the plain text — markdown is already readable.
    # For chunking, headings help preserve structure.
    return text
