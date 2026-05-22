import datetime
import json
from pathlib import Path

# Simple local JSON-based token usage log
_USAGE_LOG_PATH = Path(__file__).parent.parent.parent / "data" / "token_usage.json"


def _ensure_log():
    _USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _USAGE_LOG_PATH.exists():
        _USAGE_LOG_PATH.write_text("[]", encoding="utf-8")


def log_usage(provider: str, model: str, input_tokens: int, output_tokens: int):
    _ensure_log()
    entries = json.loads(_USAGE_LOG_PATH.read_text(encoding="utf-8"))
    entries.append({
        "timestamp": datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat(),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    })
    _USAGE_LOG_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def get_usage_summary(days: int = 7) -> dict:
    _ensure_log()
    entries = json.loads(_USAGE_LOG_PATH.read_text(encoding="utf-8"))
    cutoff = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(days=days)
    recent = [
        e for e in entries
        if datetime.datetime.fromisoformat(e["timestamp"]) >= cutoff
    ]
    return {
        "total_input_tokens": sum(e["input_tokens"] for e in recent),
        "total_output_tokens": sum(e["output_tokens"] for e in recent),
        "total_calls": len(recent),
        "provider_breakdown": _breakdown(recent),
    }


def _breakdown(entries: list[dict]) -> dict:
    breakdown = {}
    for e in entries:
        key = f"{e['provider']}/{e['model']}"
        if key not in breakdown:
            breakdown[key] = {"calls": 0, "input_tokens": 0, "output_tokens": 0}
        breakdown[key]["calls"] += 1
        breakdown[key]["input_tokens"] += e["input_tokens"]
        breakdown[key]["output_tokens"] += e["output_tokens"]
    return breakdown
