"""Sinusoidal Positional Encoding 实现。"""

from __future__ import annotations

import numpy as np


def sinusoidal_positional_encoding(sequence_length: int, d_model: int) -> np.ndarray:
    """返回形状为 [sequence_length, d_model] 的固定位置编码。"""
    if sequence_length <= 0 or d_model <= 0:
        raise ValueError("sequence_length 和 d_model 必须为正数。")

    positions = np.arange(sequence_length)[:, None]
    frequencies = np.exp(np.arange(0, d_model, 2) * (-np.log(10_000.0) / d_model))
    angles = positions * frequencies[None, :]
    encoding = np.zeros((sequence_length, d_model), dtype=np.float64)
    encoding[:, 0::2] = np.sin(angles)
    encoding[:, 1::2] = np.cos(angles[:, : d_model // 2])
    return encoding


if __name__ == "__main__":
    print(sinusoidal_positional_encoding(sequence_length=4, d_model=6))
