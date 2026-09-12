"""LLM 上下文的 Token 截断策略实现。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import numbers
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class TruncationResult(Generic[T]):
    """截断结果；truncated 单独表达是否省略内容，避免混入不同类型的伪 Token。"""

    tokens: list[T]
    truncated: bool


def truncate_tokens(tokens: Sequence[T], max_tokens: int, strategy: str = "head_tail") -> TruncationResult[T]:
    """按 head、tail 或 head_tail 策略截断 Token 序列。"""
    if not isinstance(max_tokens, numbers.Integral) or isinstance(max_tokens, bool) or max_tokens <= 0:
        raise ValueError("max_tokens 必须为正整数。")
    if strategy not in {"head", "tail", "head_tail"}:
        raise ValueError("strategy 仅支持 'head'、'tail' 或 'head_tail'。")
    values = list(tokens)
    if len(values) <= max_tokens:
        return TruncationResult(tokens=values, truncated=False)
    if strategy == "head":
        return TruncationResult(tokens=values[: int(max_tokens)], truncated=True)
    if strategy == "tail":
        return TruncationResult(tokens=values[-int(max_tokens) :], truncated=True)
    head_count = (int(max_tokens) + 1) // 2
    tail_count = int(max_tokens) - head_count
    kept = values[:head_count] + (values[-tail_count:] if tail_count else [])
    return TruncationResult(tokens=kept, truncated=True)


if __name__ == "__main__":
    input_tokens = [f"t{index}" for index in range(10)]
    print(truncate_tokens(input_tokens, max_tokens=6, strategy="head_tail"))
