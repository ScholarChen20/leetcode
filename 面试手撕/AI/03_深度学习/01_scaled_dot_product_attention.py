"""Scaled Dot-Product Attention 的 NumPy 实现。"""

from __future__ import annotations

import numpy as np


def _masked_softmax(scores: np.ndarray, mask: np.ndarray | None) -> np.ndarray:
    """计算最后一维安全 Softmax，mask 中 True 表示可见位置。

    全部被屏蔽的行返回全零权重，避免将无效位置分配为均匀概率。
    """
    if scores.ndim < 1 or scores.shape[-1] == 0:
        raise ValueError("scores 的最后一维必须包含至少一个 key。")
    if not np.all(np.isfinite(scores)):
        raise ValueError("scores 不能包含 NaN 或 Inf。")

    if mask is None:
        shifted = scores - np.max(scores, axis=-1, keepdims=True)
        values = np.exp(shifted)
        return values / values.sum(axis=-1, keepdims=True)

    try:
        valid_mask = np.broadcast_to(np.asarray(mask, dtype=bool), scores.shape)
    except ValueError as error:
        raise ValueError("mask 无法广播到 scores 的形状。") from error

    has_valid_key = valid_mask.any(axis=-1, keepdims=True)
    masked_scores = np.where(valid_mask, scores, -np.inf)
    max_scores = np.max(masked_scores, axis=-1, keepdims=True)
    max_scores = np.where(has_valid_key, max_scores, 0.0)

    shifted = np.zeros_like(scores)
    np.subtract(scores, max_scores, out=shifted, where=valid_mask)
    values = np.zeros_like(scores)
    np.exp(shifted, out=values, where=valid_mask)
    denominators = values.sum(axis=-1, keepdims=True)
    return np.divide(values, denominators, out=np.zeros_like(values), where=denominators != 0)


def scaled_dot_product_attention(
    query: np.ndarray,
    key: np.ndarray,
    value: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """返回 Attention 输出和注意力权重。

    输入最后两维依次为 [sequence_length, hidden_dimension]；前置批维度必须一致。
    """
    q = np.asarray(query, dtype=np.float64)
    k = np.asarray(key, dtype=np.float64)
    v = np.asarray(value, dtype=np.float64)
    if q.ndim < 2 or k.ndim < 2 or v.ndim < 2:
        raise ValueError("Q、K、V 至少必须包含序列维和特征维。")
    if q.shape[:-2] != k.shape[:-2] or k.shape[:-2] != v.shape[:-2]:
        raise ValueError("Q、K、V 的前置批维度必须一致。")
    if q.shape[-1] == 0 or q.shape[-1] != k.shape[-1] or k.shape[-2] != v.shape[-2]:
        raise ValueError("Q/K 的特征维度和 K/V 的序列长度必须匹配且非空。")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(k)) or not np.all(np.isfinite(v)):
        raise ValueError("Q、K、V 不能包含 NaN 或 Inf。")

    scores = q @ np.swapaxes(k, -1, -2) / np.sqrt(q.shape[-1])
    weights = _masked_softmax(scores, mask)
    return weights @ v, weights


if __name__ == "__main__":
    q = np.array([[[1.0, 0.0], [0.0, 1.0]]])
    k = q.copy()
    v = np.array([[[10.0, 0.0], [0.0, 20.0]]])
    output, attention_weights = scaled_dot_product_attention(q, k, v)
    print("注意力权重:\n", attention_weights)
    print("输出:\n", output)
