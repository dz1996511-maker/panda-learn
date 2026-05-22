import re

# Chinese sentence-ending punctuation
_CHINESE_SENTENCE_END = re.compile(r"([。！？\n])")
_CHINESE_SUB_SENTENCE = re.compile(r"([，；、：])")


def estimate_token_count(text: str) -> int:
    """Rough token estimate for Chinese text (~1.5 chars per token)."""
    return max(1, int(len(text) / 1.5))


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, respecting Chinese punctuation."""
    parts = _CHINESE_SENTENCE_END.split(text)
    sentences = []
    buf = ""
    for part in parts:
        buf += part
        if _CHINESE_SENTENCE_END.match(part):
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())
    return [s for s in sentences if s]


def split_sub_sentences(text: str) -> list[str]:
    """Split on sub-sentence boundaries (commas, etc.), keeping them short."""
    parts = _CHINESE_SUB_SENTENCE.split(text)
    result = []
    buf = ""
    for part in parts:
        buf += part
        if _CHINESE_SUB_SENTENCE.match(part):
            result.append(buf.strip())
            buf = ""
    if buf.strip():
        result.append(buf.strip())
    return [s for s in result if s]
