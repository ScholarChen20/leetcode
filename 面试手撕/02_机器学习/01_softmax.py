"""数值稳定的 Softmax 实现。"""

from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray, axis: int = -1) -> np.ndarray:
    """沿指定维度计算数值稳定的 Softmax 概率。"""
    values = np.asarray(logits, dtype=np.float64)
    shifted = values - np.max(values, axis=axis, keepdims=True)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values, axis=axis, keepdims=True)


if __name__ == "__main__":
    sample_logits = np.array([[1.0, 2.0, 3.0], [1000.0, 1001.0, 1002.0]])
    probabilities = softmax(sample_logits)
    print(probabilities)
    print("每行概率和:", probabilities.sum(axis=1))
