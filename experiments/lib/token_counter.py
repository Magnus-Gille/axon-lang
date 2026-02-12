"""
Token counter for experiment measurements.
Wraps tiktoken for cl100k_base (GPT-4) and o200k_base (GPT-4o) encodings.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=4)
def _get_encoding(name: str):
    import tiktoken
    return tiktoken.get_encoding(name)


def count_tokens(
    text: str,
    encoding: str = "cl100k_base",
) -> int:
    """Count tokens in text using specified encoding."""
    enc = _get_encoding(encoding)
    return len(enc.encode(text))


def count_tokens_multi(
    text: str,
    encodings: Optional[list[str]] = None,
) -> dict[str, int]:
    """Count tokens across multiple encodings. Returns {encoding: count}."""
    if encodings is None:
        encodings = ["cl100k_base", "o200k_base"]
    return {enc: count_tokens(text, enc) for enc in encodings}


def count_characters(text: str) -> int:
    """Count characters (for baseline comparison)."""
    return len(text)


def measure(text: str, encoding: str = "cl100k_base") -> dict:
    """Return a measurement dict with tokens, characters, and ratio."""
    tokens = count_tokens(text, encoding)
    chars = count_characters(text)
    return {
        "tokens": tokens,
        "characters": chars,
        "tokens_per_char": round(tokens / chars, 4) if chars > 0 else 0,
        "encoding": encoding,
    }
