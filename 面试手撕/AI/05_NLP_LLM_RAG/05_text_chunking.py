"""RAG 常用的文本和 Token 序列窗口切块实现。"""

from __future__ import annotations

from collections.abc import Sequence
import numbers
from typing import TypeVar


T = TypeVar("T")


def chunk_token_sequence(tokens: Sequence[T], chunk_size: int = 200, overlap: int = 40) -> list[list[T]]:
    """按真实 tokenizer 产生的 Token 序列切块，并保留相邻块重叠内容。"""
    if (
        not isinstance(chunk_size, numbers.Integral)
        or isinstance(chunk_size, bool)
        or not isinstance(overlap, numbers.Integral)
        or isinstance(overlap, bool)
        or chunk_size <= 0
        or overlap < 0
        or overlap >= chunk_size
    ):
        raise ValueError("chunk_size 必须为正整数，overlap 必须满足 0 <= overlap < chunk_size。")
    values = list(tokens)
    if not values:
        return []

    chunks: list[list[T]] = []
    start = 0
    while start < len(values):
        end = min(start + int(chunk_size), len(values))
        chunks.append(values[start:end])
        if end == len(values):
            break
        start = end - int(overlap)
    return chunks


def chunk_text_by_whitespace(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """按空白词切块，仅适合空白分词语言或演示；中文应传入真实 tokenizer 的结果。"""
    if not isinstance(text, str):
        raise ValueError("text 必须是字符串。")
    return [" ".join(chunk) for chunk in chunk_token_sequence(text.split(), chunk_size, overlap)]


if __name__ == "__main__":
    sample = " ".join(f"token_{index}" for index in range(1, 21))
    for index, chunk in enumerate(chunk_text_by_whitespace(sample, chunk_size=8, overlap=2), start=1):
        print(f"Chunk {index}: {chunk}")
