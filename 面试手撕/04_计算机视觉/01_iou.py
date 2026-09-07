"""目标检测框的 Pairwise IoU 实现。"""

from __future__ import annotations

import numpy as np


def _as_valid_box_matrix(boxes: np.ndarray, name: str) -> np.ndarray:
    """转换并验证连续坐标系中的 xyxy 框矩阵。"""
    values = np.asarray(boxes, dtype=np.float64)
    if values.ndim == 1:
        values = values[None, :]
    if values.ndim != 2 or values.shape[1] != 4 or not np.all(np.isfinite(values)):
        raise ValueError(f"{name} 必须是仅含有限数值的 [N, 4] xyxy 数组。")
    if np.any(values[:, 2] < values[:, 0]) or np.any(values[:, 3] < values[:, 1]):
        raise ValueError(f"{name} 的右下坐标不能小于左上坐标。")
    return values


def pairwise_iou(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    """计算两组连续 xyxy 检测框的两两 IoU，返回形状 [N, M]。"""
    a = _as_valid_box_matrix(boxes_a, "boxes_a")
    b = _as_valid_box_matrix(boxes_b, "boxes_b")
    top_left = np.maximum(a[:, None, :2], b[None, :, :2])
    bottom_right = np.minimum(a[:, None, 2:], b[None, :, 2:])
    intersection_wh = np.maximum(bottom_right - top_left, 0.0)
    intersection = intersection_wh[..., 0] * intersection_wh[..., 1]

    area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    union = area_a[:, None] + area_b[None, :] - intersection
    return np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)


if __name__ == "__main__":
    first = np.array([[0, 0, 2, 2], [0, 0, 1, 1]], dtype=float)
    second = np.array([[1, 1, 3, 3], [0, 0, 2, 2]], dtype=float)
    print(pairwise_iou(first, second))
