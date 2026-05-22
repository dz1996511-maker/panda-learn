from app.knowledge.parsers.txt_parser import parse_txt
from app.knowledge.parsers.pdf_parser import parse_pdf
from app.knowledge.parsers.markdown_parser import parse_markdown
from app.knowledge.parsers.html_parser import parse_html


PARSER_MAP = {
    "txt": parse_txt,
    "md": parse_markdown,
    "html": parse_html,
    "pdf": parse_pdf,
}


def get_parser(file_type: str):
    parser = PARSER_MAP.get(file_type)
    if parser is None:
        raise ValueError(f"Unsupported file type: {file_type}")
    return parser
