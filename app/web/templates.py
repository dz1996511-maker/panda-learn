import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.templating import Jinja2Templates

TEMPLATE_DIR = Path(__file__).parent / "templates"


def from_json(value):
    """Jinja2 filter to parse JSON string."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return value


_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)
_env.filters["from_json"] = from_json

templates = Jinja2Templates(env=_env)
