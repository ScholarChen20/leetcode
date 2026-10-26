"""决策树单节点最佳 Gini 划分实现。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SplitResult:
    """最佳划分结果。"""

    feature_index: int
    threshold: float
    gini: float
    left_indices: np.ndarray
    right_indices: np.ndarray


def gini_impurity(labels: np.ndarray) -> float:
    """计算一维标签节点的 Gini 不纯度。"""
    y = np.asarray(labels)
    if y.ndim != 1:
        raise ValueError("labels 必须是一维数组。")
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probabilities = counts / len(y)
    return float(1.0 - np.sum(probabilities**2))


def best_gini_split(features: np.ndarray, labels: np.ndarray) -> SplitResult | None:
    """遍历所有特征和相邻值中点，寻找加权 Gini 最小的二叉划分。"""
    x = np.asarray(features, dtype=np.float64)
    y = np.asarray(labels)
    if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] == 0 or y.shape != (x.shape[0],):
        raise ValueError("features 必须是非空二维数组，labels 必须是一维且样本数一致。")
    if not np.all(np.isfinite(x)):
        raise ValueError("features 不能包含 NaN 或 Inf；缺失值应先按业务规则处理。")

    sample_count = x.shape[0]
    best: SplitResult | None = None
    for feature_index in range(x.shape[1]):
        unique_values = np.unique(x[:, feature_index])
        thresholds = unique_values[:-1] / 2.0 + unique_values[1:] / 2.0
        for threshold in thresholds:
            left_indices = np.where(x[:, feature_index] <= threshold)[0]
            right_indices = np.where(x[:, feature_index] > threshold)[0]
            if len(left_indices) == 0 or len(right_indices) == 0:
                continue
            weighted_gini = (
                len(left_indices) / sample_count * gini_impurity(y[left_indices])
                + len(right_indices) / sample_count * gini_impurity(y[right_indices])
            )
            if best is None or weighted_gini < best.gini:
                best = SplitResult(feature_index, float(threshold), float(weighted_gini), left_indices, right_indices)
    return best


if __name__ == "__main__":
    x_train = np.array([[2.0, 1.0], [3.0, 1.5], [8.0, 7.0], [9.0, 8.0]])
    y_train = np.array([0, 0, 1, 1])
    print(best_gini_split(x_train, y_train))
