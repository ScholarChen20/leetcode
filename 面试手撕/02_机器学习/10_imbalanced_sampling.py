"""类别不平衡中的随机过采样、欠采样和类别权重计算。"""

from __future__ import annotations

import math
import numbers

import numpy as np


def _validate_labels(labels: np.ndarray) -> np.ndarray:
    """验证非空、一维且可安全比较的类别标签。"""
    y = np.asarray(labels)
    if y.ndim != 1 or len(y) == 0:
        raise ValueError("labels 必须是非空一维数组。")
    if np.issubdtype(y.dtype, np.number):
        numeric_labels = np.asarray(y, dtype=np.float64)
        if not np.all(np.isfinite(numeric_labels)):
            raise ValueError("数值 labels 不能包含 NaN 或 Inf。")
    elif y.dtype == object:
        for label in y:
            if isinstance(label, numbers.Real) and not math.isfinite(float(label)):
                raise ValueError("对象 labels 不能包含 NaN 或 Inf。")
    try:
        np.unique(y)
    except TypeError as error:
        raise ValueError("labels 必须是同类型且可比较的类别值。") from error
    return y


def _validate_samples(features: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """验证样本数一致且标签为非空一维数组。"""
    x = np.asarray(features)
    y = _validate_labels(labels)
    if x.ndim == 0 or x.shape[0] != y.shape[0]:
        raise ValueError("features 必须至少一维，且样本数必须与 labels 一致。")
    return x, y


def random_oversample(
    features: np.ndarray,
    labels: np.ndarray,
    random_state: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """保留全部原样本，并将少数类补样到多数类规模。"""
    x, y = _validate_samples(features, labels)
    rng = np.random.default_rng(random_state)
    classes, counts = np.unique(y, return_counts=True)
    target_count = int(counts.max())
    selected: list[np.ndarray] = []
    for category in classes:
        indices = np.where(y == category)[0]
        if len(indices) == 0:
            raise ValueError("类别标签无法可靠匹配样本。")
        if len(indices) < target_count:
            extra_indices = rng.choice(indices, size=target_count - len(indices), replace=True)
            indices = np.concatenate((indices, extra_indices))
        selected.append(indices)
    merged = np.concatenate(selected)
    if len(merged) != len(classes) * target_count:
        raise RuntimeError("过采样结果长度异常。")
    rng.shuffle(merged)
    return x[merged], y[merged]


def random_undersample(
    features: np.ndarray,
    labels: np.ndarray,
    random_state: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """将各类别随机下采样到少数类规模。"""
    x, y = _validate_samples(features, labels)
    rng = np.random.default_rng(random_state)
    classes, counts = np.unique(y, return_counts=True)
    target_count = int(counts.min())
    selected = [rng.choice(np.where(y == category)[0], size=target_count, replace=False) for category in classes]
    merged = np.concatenate(selected)
    rng.shuffle(merged)
    return x[merged], y[merged]


def balanced_class_weights(labels: np.ndarray) -> dict[object, float]:
    """返回 n_samples / (n_classes * class_count) 形式的平衡类别权重。"""
    y = _validate_labels(labels)
    classes, counts = np.unique(y, return_counts=True)
    return {
        category.item() if hasattr(category, "item") else category: len(y) / (len(classes) * count)
        for category, count in zip(classes, counts)
    }


if __name__ == "__main__":
    x_train = np.arange(20).reshape(10, 2)
    y_train = np.array([0] * 8 + [1] * 2)
    _, over_labels = random_oversample(x_train, y_train, random_state=42)
    _, under_labels = random_undersample(x_train, y_train, random_state=42)
    print("类别权重:", balanced_class_weights(y_train))
    print("过采样后:", np.unique(over_labels, return_counts=True))
    print("欠采样后:", np.unique(under_labels, return_counts=True))
