from lxml import html as lxml_html


def parse_html(content: bytes) -> str:
    """Parse HTML content, extracting readable text."""
    root = lxml_html.fromstring(content)
    # Remove script and style elements
    for tag in root.xpath("//script | //style | //nav | //footer"):
        tag.getparent().remove(tag)
    text = root.text_content()
    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
