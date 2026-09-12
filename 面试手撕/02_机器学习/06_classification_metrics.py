"""二分类 Precision、Recall、F1 和混淆矩阵实现。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BinaryMetrics:
    """二分类评估结果。"""

    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float
    accuracy: float


def _validate_binary_labels(values: np.ndarray, name: str) -> np.ndarray:
    """验证非空一维 0/1 整数标签，避免浮点值被静默截断。"""
    raw = np.asarray(values)
    if raw.ndim != 1 or len(raw) == 0 or not np.issubdtype(raw.dtype, np.number) or np.issubdtype(raw.dtype, np.bool_):
        raise ValueError(f"{name} 必须是非空一维数值标签数组。")
    numeric = np.asarray(raw, dtype=np.float64)
    if not np.all(np.isfinite(numeric)) or not np.array_equal(numeric, np.floor(numeric)) or not np.all(np.isin(numeric, [0.0, 1.0])):
        raise ValueError(f"{name} 必须只包含整数 0 或 1。")
    return numeric.astype(np.int64)


def binary_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> BinaryMetrics:
    """计算二分类混淆矩阵及常见指标，正类标签为 1。"""
    truth = _validate_binary_labels(y_true, "y_true")
    prediction = _validate_binary_labels(y_pred, "y_pred")
    if truth.shape != prediction.shape:
        raise ValueError("y_true 和 y_pred 必须形状一致。")

    tp = int(np.sum((truth == 1) & (prediction == 1)))
    fp = int(np.sum((truth == 0) & (prediction == 1)))
    tn = int(np.sum((truth == 0) & (prediction == 0)))
    fn = int(np.sum((truth == 1) & (prediction == 0)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(truth)
    return BinaryMetrics(tp, fp, tn, fn, precision, recall, f1, accuracy)


if __name__ == "__main__":
    result = binary_classification_metrics(
        np.array([1, 1, 0, 0, 1, 0]),
        np.array([1, 0, 1, 0, 1, 0]),
    )
    print(result)
