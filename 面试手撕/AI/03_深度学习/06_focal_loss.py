"""二分类 Focal Loss 实现。"""

from __future__ import annotations

import math

import numpy as np


def binary_focal_loss(
    logits: np.ndarray,
    targets: np.ndarray,
    alpha: float = 0.25,
    gamma: float = 2.0,
    reduction: str = "mean",
) -> float | np.ndarray:
    """根据 logits 和二分类标签计算数值稳定的 Focal Loss。

    使用 log-sigmoid 计算 ``log(p_t)``，避免大幅错误 logits 被概率裁剪后
    静默封顶。例如 ``logit=1000, target=0`` 仍会产生约 750 的损失。
    """
    scores = np.asarray(logits, dtype=np.float64)
    labels = np.asarray(targets, dtype=np.float64)
    if scores.shape != labels.shape or scores.size == 0 or not np.all(np.isfinite(scores)) or not np.all(np.isfinite(labels)):
        raise ValueError("logits 和 targets 必须形状一致、非空且仅含有限数值。")
    if not np.all(np.isin(labels, [0.0, 1.0])):
        raise ValueError("targets 必须是 0 或 1。")
    if (
        not math.isfinite(float(alpha))
        or not math.isfinite(float(gamma))
        or not 0.0 <= alpha <= 1.0
        or gamma < 0
    ):
        raise ValueError("alpha 必须在 [0, 1]，gamma 必须为非负有限数。")

    # log(sigmoid(x)) 与 log(1-sigmoid(x)) 的稳定形式。
    log_positive = -np.logaddexp(0.0, -scores)
    log_negative = -np.logaddexp(0.0, scores)
    log_p_t = np.where(labels == 1.0, log_positive, log_negative)
    log_one_minus_p_t = np.where(labels == 1.0, log_negative, log_positive)
    alpha_t = np.where(labels == 1.0, float(alpha), 1.0 - float(alpha))
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        focusing_factor = np.exp(float(gamma) * log_one_minus_p_t)
        losses = -alpha_t * focusing_factor * log_p_t
    if not np.all(np.isfinite(losses)):
        raise ValueError("输入数值范围导致 Focal Loss 溢出；请缩放 logits 或使用更高精度。")

    if reduction == "none":
        return losses
    if reduction == "sum":
        with np.errstate(over="ignore", invalid="ignore"):
            reduced = float(losses.sum())
    elif reduction == "mean":
        with np.errstate(over="ignore", invalid="ignore"):
            reduced = float(losses.mean())
    else:
        raise ValueError("reduction 仅支持 'none'、'sum' 或 'mean'。")
    if not math.isfinite(reduced):
        raise ValueError("Focal Loss 聚合结果溢出；请降低 batch 大小或使用更高精度。")
    return reduced


if __name__ == "__main__":
    logits = np.array([3.0, -1.0, 0.2, -2.0])
    labels = np.array([1, 0, 1, 0])
    print("Focal Loss:", binary_focal_loss(logits, labels))
