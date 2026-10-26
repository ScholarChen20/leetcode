"""Multi-Head Attention 的前向计算实现。"""

from __future__ import annotations

import numbers

import numpy as np


def _masked_softmax(scores: np.ndarray, mask: np.ndarray | None) -> np.ndarray:
    """计算安全 masked softmax；全屏蔽行返回全零。"""
    if scores.shape[-1] == 0 or not np.all(np.isfinite(scores)):
        raise ValueError("scores 的最后一维必须非空且不含 NaN/Inf。")
    if mask is None:
        shifted = scores - np.max(scores, axis=-1, keepdims=True)
        values = np.exp(shifted)
        return values / values.sum(axis=-1, keepdims=True)
    try:
        valid_mask = np.broadcast_to(np.asarray(mask, dtype=bool), scores.shape)
    except ValueError as error:
        raise ValueError("mask 无法广播到多头注意力分数形状。") from error

    has_valid_key = valid_mask.any(axis=-1, keepdims=True)
    max_scores = np.max(np.where(valid_mask, scores, -np.inf), axis=-1, keepdims=True)
    max_scores = np.where(has_valid_key, max_scores, 0.0)
    shifted = np.zeros_like(scores)
    np.subtract(scores, max_scores, out=shifted, where=valid_mask)
    values = np.zeros_like(scores)
    np.exp(shifted, out=values, where=valid_mask)
    denominators = values.sum(axis=-1, keepdims=True)
    return np.divide(values, denominators, out=np.zeros_like(values), where=denominators != 0)


class MultiHeadAttention:
    """仅实现前向传播的多头注意力层。"""

    def __init__(self, embed_dim: int, num_heads: int, random_state: int | None = None) -> None:
        if (
            not isinstance(embed_dim, numbers.Integral)
            or isinstance(embed_dim, bool)
            or not isinstance(num_heads, numbers.Integral)
            or isinstance(num_heads, bool)
            or embed_dim <= 0
            or num_heads <= 0
            or embed_dim % num_heads != 0
        ):
            raise ValueError("embed_dim 必须能被 num_heads 整除，且两者为正整数。")
        self.embed_dim = int(embed_dim)
        self.num_heads = int(num_heads)
        self.head_dim = self.embed_dim // self.num_heads
        rng = np.random.default_rng(random_state)
        scale = 1.0 / np.sqrt(self.embed_dim)
        self.w_q = rng.normal(0.0, scale, size=(self.embed_dim, self.embed_dim))
        self.w_k = rng.normal(0.0, scale, size=(self.embed_dim, self.embed_dim))
        self.w_v = rng.normal(0.0, scale, size=(self.embed_dim, self.embed_dim))
        self.w_o = rng.normal(0.0, scale, size=(self.embed_dim, self.embed_dim))

    def forward(
        self,
        query: np.ndarray,
        key: np.ndarray,
        value: np.ndarray,
        mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """计算形状为 [batch, sequence, embed_dim] 的注意力输出。"""
        q_input = np.asarray(query, dtype=np.float64)
        k_input = np.asarray(key, dtype=np.float64)
        v_input = np.asarray(value, dtype=np.float64)
        if q_input.ndim != 3 or k_input.ndim != 3 or v_input.ndim != 3:
            raise ValueError("Q、K、V 必须是三维数组。")
        if q_input.shape[0] != k_input.shape[0] or k_input.shape[0] != v_input.shape[0]:
            raise ValueError("Q、K、V 的 batch 维度必须一致。")
        if q_input.shape[2] != self.embed_dim or k_input.shape[2] != self.embed_dim or v_input.shape[2] != self.embed_dim:
            raise ValueError("输入最后一维必须等于 embed_dim。")
        if k_input.shape[1] == 0 or k_input.shape[1] != v_input.shape[1]:
            raise ValueError("K 与 V 的非空序列长度必须一致。")
        if not np.all(np.isfinite(q_input)) or not np.all(np.isfinite(k_input)) or not np.all(np.isfinite(v_input)):
            raise ValueError("Q、K、V 不能包含 NaN 或 Inf。")

        batch_size, query_length, _ = q_input.shape
        key_length = k_input.shape[1]
        q = (q_input @ self.w_q).reshape(batch_size, query_length, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        k = (k_input @ self.w_k).reshape(batch_size, key_length, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)
        v = (v_input @ self.w_v).reshape(batch_size, key_length, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)

        scores = q @ np.swapaxes(k, -1, -2) / np.sqrt(self.head_dim)
        weights = _masked_softmax(scores, mask)
        context = weights @ v
        merged = context.transpose(0, 2, 1, 3).reshape(batch_size, query_length, self.embed_dim)
        return merged @ self.w_o


if __name__ == "__main__":
    inputs = np.array([[[1.0, 0.0, 0.5, 0.2], [0.0, 1.0, 0.3, 0.8]]])
    attention = MultiHeadAttention(embed_dim=4, num_heads=2, random_state=42)
    print(attention.forward(inputs, inputs, inputs))
