from app.utils.text_utils import estimate_token_count, split_sentences
from app.config import settings


def chunk_text(text: str, target_tokens: int | None = None, overlap_tokens: int | None = None) -> list[dict]:
    """Split text into overlapping chunks optimized for Chinese text.

    Each chunk dict: {"index": int, "content": str, "token_count": int}
    """
    target = target_tokens or settings.chunk_target_tokens
    overlap = overlap_tokens or settings.chunk_overlap_tokens

    sentences = split_sentences(text)
    chunks: list[dict] = []
    current_chunks_texts: list[str] = []
    current_token_count = 0

    for sentence in sentences:
        sent_tokens = estimate_token_count(sentence)

        if current_token_count + sent_tokens > target and current_chunks_texts:
            # Save current chunk
            content = "".join(current_chunks_texts)
            chunks.append({
                "index": len(chunks),
                "content": content,
                "token_count": current_token_count,
            })

            # Keep overlap: drop sentences from the front until under overlap
            overlap_texts = list(current_chunks_texts)
            overlap_target_tokens = 0
            while overlap_texts and overlap_target_tokens < overlap:
                overlap_target_tokens += estimate_token_count(overlap_texts[0])
                if overlap_target_tokens <= overlap:
                    overlap_texts.pop(0)
                else:
                    break
            current_chunks_texts = overlap_texts
            current_token_count = overlap_target_tokens

        current_chunks_texts.append(sentence)
        current_token_count += sent_tokens

    # Final chunk
    if current_chunks_texts:
        content = "".join(current_chunks_texts)
        chunks.append({
            "index": len(chunks),
            "content": content,
            "token_count": current_token_count,
        })

    return chunks
