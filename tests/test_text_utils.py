"""Tests for text utility functions."""

from app.utils.text_utils import estimate_token_count, split_sentences


def test_estimate_token_count():
    assert estimate_token_count("你好世界") == 2  # 4 chars / 1.5 = 2.66 -> 2
    assert estimate_token_count("") == 1


def test_split_sentences():
    text = "今天天气真好。我们去公园吧！你准备好了吗？"
    result = split_sentences(text)
    assert len(result) == 3
    assert "今天天气真好。" in result


def test_split_sentences_no_punct():
    assert split_sentences("你好") == ["你好"]


def test_split_sentences_with_newline():
    text = "第一行。\n第二行。"
    result = split_sentences(text)
    assert len(result) == 2
