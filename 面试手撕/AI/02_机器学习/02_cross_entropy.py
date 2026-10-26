"""多分类交叉熵损失及其对 logits 的梯度实现。"""

from __future__ import annotations

import numpy as np


def _validate_multiclass_inputs(logits: np.ndarray, targets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """验证有限 logits 和整型类别索引，避免 NumPy 负索引等静默错误。"""
    scores = np.asarray(logits, dtype=np.float64)
    raw_labels = np.asarray(targets)
    if scores.ndim != 2 or scores.shape[0] == 0 or scores.shape[1] == 0 or not np.all(np.isfinite(scores)):
        raise ValueError("logits 必须是非空且仅含有限数值的 [batch_size, num_classes] 数组。")
    if raw_labels.shape != (scores.shape[0],) or not np.issubdtype(raw_labels.dtype, np.number) or np.issubdtype(raw_labels.dtype, np.bool_):
        raise ValueError("targets 必须是形状为 [batch_size] 的数值类别索引数组。")
    numeric_labels = np.asarray(raw_labels, dtype=np.float64)
    if not np.all(np.isfinite(numeric_labels)) or not np.array_equal(numeric_labels, np.floor(numeric_labels)):
        raise ValueError("targets 必须是有限整数类别索引。")
    if np.any(numeric_labels < 0) or np.any(numeric_labels >= scores.shape[1]):
        raise ValueError("targets 中存在越界的类别索引。")
    return scores, numeric_labels.astype(np.int64)


def cross_entropy_loss(
    logits: np.ndarray,
    targets: np.ndarray,
    reduction: str = "mean",
) -> float | np.ndarray:
    """计算类别索引标签对应的数值稳定交叉熵。"""
    scores, labels = _validate_multiclass_inputs(logits, targets)
    shifted = scores - np.max(scores, axis=1, keepdims=True)
    log_probabilities = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    losses = -log_probabilities[np.arange(scores.shape[0]), labels]
    if reduction == "none":
        return losses
    if reduction == "sum":
        return float(losses.sum())
    if reduction == "mean":
        return float(losses.mean())
    raise ValueError("reduction 仅支持 'none'、'sum' 或 'mean'。")


def cross_entropy_gradient(logits: np.ndarray, targets: np.ndarray) -> np.ndarray:
    """返回平均交叉熵对 logits 的梯度。"""
    scores, labels = _validate_multiclass_inputs(logits, targets)
    shifted = scores - np.max(scores, axis=1, keepdims=True)
    probabilities = np.exp(shifted)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    probabilities[np.arange(scores.shape[0]), labels] -= 1.0
    return probabilities / scores.shape[0]


if __name__ == "__main__":
    sample_logits = np.array([[2.0, 1.0, 0.1], [0.5, 1.2, 2.0]])
    sample_targets = np.array([0, 2])
    print("loss:", cross_entropy_loss(sample_logits, sample_targets))
    print("gradient:\n", cross_entropy_gradient(sample_logits, sample_targets))
