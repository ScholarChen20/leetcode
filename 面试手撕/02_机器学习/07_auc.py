"""使用秩统计法实现二分类 ROC-AUC。"""

from __future__ import annotations

import numpy as np


def _validate_binary_labels(values: np.ndarray) -> np.ndarray:
    """验证非空一维 0/1 整数标签。"""
    raw = np.asarray(values)
    if raw.ndim != 1 or len(raw) == 0 or not np.issubdtype(raw.dtype, np.number) or np.issubdtype(raw.dtype, np.bool_):
        raise ValueError("y_true 必须是非空一维数值标签数组。")
    numeric = np.asarray(raw, dtype=np.float64)
    if not np.all(np.isfinite(numeric)) or not np.array_equal(numeric, np.floor(numeric)) or not np.all(np.isin(numeric, [0.0, 1.0])):
        raise ValueError("y_true 必须只包含整数 0 和 1。")
    return numeric.astype(np.int64)


def roc_auc_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """计算二分类 ROC-AUC，正确处理预测分数并列的情况。"""
    labels = _validate_binary_labels(y_true)
    scores = np.asarray(y_score, dtype=np.float64)
    if scores.shape != labels.shape or scores.ndim != 1 or not np.all(np.isfinite(scores)):
        raise ValueError("y_score 必须是一维、形状匹配且仅含有限数值。")

    positive_count = int(labels.sum())
    negative_count = len(labels) - positive_count
    if positive_count == 0 or negative_count == 0:
        raise ValueError("AUC 计算必须同时包含正负样本。")

    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), dtype=np.float64)
    start = 0
    while start < len(scores):
        end = start + 1
        while end < len(scores) and scores[order[end]] == scores[order[start]]:
            end += 1
        average_rank = (start + 1 + end) / 2.0
        ranks[order[start:end]] = average_rank
        start = end

    positive_rank_sum = ranks[labels == 1].sum()
    return float((positive_rank_sum - positive_count * (positive_count + 1) / 2) / (positive_count * negative_count))


if __name__ == "__main__":
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.4, 0.35, 0.8])
    print("AUC:", roc_auc_score(labels, scores))
