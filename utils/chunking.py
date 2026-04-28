"""Content chunking helpers."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving readable sentences."""
    return re.sub(r"\s+", " ", text or "").strip()


def chunk_text(text: str, max_words: int = 120) -> list[str]:
    """Split text into paragraph/sentence-sized chunks for downstream processing."""
    text = clean_text(text)
    if not text:
        return []

    paragraphs = [clean_text(part) for part in re.split(r"\n{2,}", text) if clean_text(part)]
    if len(paragraphs) <= 1:
        paragraphs = [clean_text(part) for part in re.split(r"(?<=[.!?])\s+", text) if clean_text(part)]

    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for part in paragraphs:
        words = part.split()
        if current and current_words + len(words) > max_words:
            chunks.append(" ".join(current))
            current = []
            current_words = 0
        current.append(part)
        current_words += len(words)

    if current:
        chunks.append(" ".join(current))

    return chunks
