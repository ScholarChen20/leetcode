"""Transformer 中的 Causal Mask 和 Padding Mask 实现。"""

from __future__ import annotations

import numpy as np


def causal_mask(sequence_length: int) -> np.ndarray:
    """返回下三角因果掩码，True 表示当前位置可见。"""
    if sequence_length <= 0:
        raise ValueError("sequence_length 必须为正数。")
    return np.tril(np.ones((sequence_length, sequence_length), dtype=bool))


def padding_mask(token_ids: np.ndarray, pad_token_id: int = 0) -> np.ndarray:
    """返回形状 [batch, 1, 1, sequence] 的 Padding Mask。"""
    tokens = np.asarray(token_ids)
    if tokens.ndim != 2:
        raise ValueError("token_ids 必须是形状为 [batch, sequence] 的二维数组。")
    return (tokens != pad_token_id)[:, None, None, :]


def decoder_self_attention_mask(token_ids: np.ndarray, pad_token_id: int = 0) -> np.ndarray:
    """组合 Padding Mask 和 Causal Mask，适用于 Decoder 自注意力。"""
    tokens = np.asarray(token_ids)
    padding = padding_mask(tokens, pad_token_id)
    causal = causal_mask(tokens.shape[1])[None, None, :, :]
    return padding & causal


if __name__ == "__main__":
    ids = np.array([[5, 7, 9, 0], [3, 4, 0, 0]])
    print("Causal Mask:\n", causal_mask(4).astype(int))
    print("Decoder Mask:\n", decoder_self_attention_mask(ids).astype(int))
