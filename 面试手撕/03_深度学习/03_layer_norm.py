"""Layer Normalization 实现。"""

from __future__ import annotations

import math

import numpy as np


def layer_norm(
    inputs: np.ndarray,
    gamma: np.ndarray | None = None,
    beta: np.ndarray | None = None,
    eps: float = 1e-5,
) -> np.ndarray:
    """沿最后一维归一化，gamma 和 beta 形状应与最后一维一致。"""
    if not math.isfinite(float(eps)) or eps <= 0:
        raise ValueError("eps 必须为有限正数。")
    x = np.asarray(inputs, dtype=np.float64)
    if x.ndim == 0 or x.shape[-1] == 0 or not np.all(np.isfinite(x)):
        raise ValueError("inputs 至少应有一个非空特征维，且不能包含 NaN/Inf。")
    feature_dim = x.shape[-1]
    scale = np.ones(feature_dim) if gamma is None else np.asarray(gamma, dtype=np.float64)
    shift = np.zeros(feature_dim) if beta is None else np.asarray(beta, dtype=np.float64)
    if (
        scale.shape != (feature_dim,)
        or shift.shape != (feature_dim,)
        or not np.all(np.isfinite(scale))
        or not np.all(np.isfinite(shift))
    ):
        raise ValueError("gamma 和 beta 必须与最后一维长度一致且仅含有限数值。")

    mean = x.mean(axis=-1, keepdims=True)
    variance = x.var(axis=-1, keepdims=True)
    normalized = (x - mean) / np.sqrt(variance + eps)
    return normalized * scale + shift


if __name__ == "__main__":
    sample = np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]])
    print(layer_norm(sample))
