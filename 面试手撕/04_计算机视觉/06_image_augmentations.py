"""带检测框同步变换的基础图像增强实现。"""

from __future__ import annotations

import math
import numbers

import numpy as np


def _validate_xyxy_boxes(boxes: np.ndarray) -> np.ndarray:
    """验证连续坐标系下的 xyxy 检测框。"""
    transformed = np.asarray(boxes, dtype=np.float64).copy()
    if transformed.ndim != 2 or transformed.shape[1] != 4 or not np.all(np.isfinite(transformed)):
        raise ValueError("boxes 必须是形状为 [N, 4] 且仅含有限数值的 xyxy 数组。")
    if np.any(transformed[:, 2] < transformed[:, 0]) or np.any(transformed[:, 3] < transformed[:, 1]):
        raise ValueError("检测框的右下坐标不能小于左上坐标。")
    return transformed


def horizontal_flip(image: np.ndarray, boxes: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray | None]:
    """左右翻转 HWC 图像，并同步变换右下角开区间的 xyxy 检测框。"""
    source = np.asarray(image)
    if source.ndim != 3 or source.shape[0] == 0 or source.shape[1] == 0:
        raise ValueError("image 必须是高宽非空的 HWC 三维数组。")
    flipped_image = source[:, ::-1, :].copy()
    if boxes is None:
        return flipped_image, None

    transformed = _validate_xyxy_boxes(boxes)
    width = source.shape[1]
    old_x1 = transformed[:, 0].copy()
    transformed[:, 0] = width - transformed[:, 2]
    transformed[:, 2] = width - old_x1
    return flipped_image, transformed


def adjust_brightness(image: np.ndarray, delta: float) -> np.ndarray:
    """对 [0, 255] 图像增加有限亮度偏移并裁剪。"""
    if not math.isfinite(float(delta)):
        raise ValueError("delta 必须是有限数值。")
    return np.clip(np.asarray(image, dtype=np.float64) + delta, 0, 255).astype(np.uint8)


def resize_nearest(image: np.ndarray, output_shape: tuple[int, int]) -> np.ndarray:
    """使用像素中心映射的最近邻插值缩放 HWC 图像。"""
    source = np.asarray(image)
    try:
        target_h, target_w = output_shape
    except (TypeError, ValueError) as error:
        raise ValueError("output_shape 必须是 (height, width)。") from error
    if (
        source.ndim != 3
        or source.shape[0] == 0
        or source.shape[1] == 0
        or not isinstance(target_h, numbers.Integral)
        or isinstance(target_h, bool)
        or not isinstance(target_w, numbers.Integral)
        or isinstance(target_w, bool)
        or target_h <= 0
        or target_w <= 0
    ):
        raise ValueError("image 必须是非空 HWC，输出高宽必须为正整数。")

    target_h, target_w = int(target_h), int(target_w)
    row_indices = np.floor((np.arange(target_h) + 0.5) * source.shape[0] / target_h).astype(int)
    col_indices = np.floor((np.arange(target_w) + 0.5) * source.shape[1] / target_w).astype(int)
    row_indices = np.minimum(row_indices, source.shape[0] - 1)
    col_indices = np.minimum(col_indices, source.shape[1] - 1)
    return source[row_indices][:, col_indices]


if __name__ == "__main__":
    image = np.arange(3 * 4 * 3, dtype=np.uint8).reshape(3, 4, 3)
    boxes = np.array([[0, 0, 2, 2]], dtype=float)
    _, flipped_boxes = horizontal_flip(image, boxes)
    print("翻转后的框:", flipped_boxes)
    print("缩放后的图像形状:", resize_nearest(image, (6, 8)).shape)
