"""Inverted Dropout 实现。"""

from __future__ import annotations

import numpy as np


def dropout(
    inputs: np.ndarray,
    drop_rate: float = 0.5,
    training: bool = True,
    random_state: int | None = None,
) -> np.ndarray:
    """训练阶段随机置零并按保留率缩放；推理阶段原样返回。"""
    if not 0.0 <= drop_rate < 1.0:
        raise ValueError("drop_rate 必须位于 [0, 1) 区间。")
    x = np.asarray(inputs, dtype=np.float64)
    if not training or drop_rate == 0.0:
        return x.copy()

    keep_probability = 1.0 - drop_rate
    rng = np.random.default_rng(random_state)
    mask = rng.random(x.shape) < keep_probability
    return x * mask / keep_probability


if __name__ == "__main__":
    values = np.ones((3, 5))
    print("训练阶段:\n", dropout(values, drop_rate=0.4, training=True, random_state=42))
    print("推理阶段:\n", dropout(values, drop_rate=0.4, training=False))
