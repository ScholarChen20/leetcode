"""YOLO Letterbox 后的检测框坐标还原实现。"""

from __future__ import annotations

from dataclasses import dataclass
import numbers

import numpy as np


@dataclass(frozen=True)
class LetterboxTransform:
    """按整数 resize 与左右/上下分配 padding 得到的实际变换参数。"""

    scale_x: float
    scale_y: float
    pad_left: int
    pad_top: int
    resized_shape: tuple[int, int]


def _validate_shape(shape: tuple[int, int], name: str) -> tuple[int, int]:
    """验证图像形状为 (height, width) 的正整数。"""
    try:
        height, width = shape
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} 必须是 (height, width)。") from error
    if (
        not isinstance(height, numbers.Integral)
        or isinstance(height, bool)
        or not isinstance(width, numbers.Integral)
        or isinstance(width, bool)
        or height <= 0
        or width <= 0
    ):
        raise ValueError(f"{name} 的高宽必须为正整数。")
    return int(height), int(width)


def letterbox_parameters(
    original_shape: tuple[int, int],
    input_shape: tuple[int, int],
) -> LetterboxTransform:
    """返回与整数 resize + 对称 padding 完全一致的实际 Letterbox 变换参数。"""
    original_h, original_w = _validate_shape(original_shape, "original_shape")
    input_h, input_w = _validate_shape(input_shape, "input_shape")
    ratio = min(input_w / original_w, input_h / original_h)
    resized_w = max(1, round(original_w * ratio))
    resized_h = max(1, round(original_h * ratio))
    pad_left = (input_w - resized_w) // 2
    pad_top = (input_h - resized_h) // 2
    return LetterboxTransform(
        scale_x=resized_w / original_w,
        scale_y=resized_h / original_h,
        pad_left=pad_left,
        pad_top=pad_top,
        resized_shape=(resized_h, resized_w),
    )


def restore_letterbox_boxes(
    boxes: np.ndarray,
    original_shape: tuple[int, int],
    input_shape: tuple[int, int],
) -> np.ndarray:
    """把整数 Letterbox 输入空间中的连续 xyxy 框还原到原图并裁剪边界。"""
    result = np.asarray(boxes, dtype=np.float64).copy()
    if result.ndim == 1:
        result = result[None, :]
    if (
        result.ndim != 2
        or result.shape[1] != 4
        or not np.all(np.isfinite(result))
        or np.any(result[:, 2] < result[:, 0])
        or np.any(result[:, 3] < result[:, 1])
    ):
        raise ValueError("boxes 必须是仅含有限数值的 [N, 4] 有效 xyxy 数组。")

    original_h, original_w = _validate_shape(original_shape, "original_shape")
    transform = letterbox_parameters(original_shape, input_shape)
    result[:, [0, 2]] = (result[:, [0, 2]] - transform.pad_left) / transform.scale_x
    result[:, [1, 3]] = (result[:, [1, 3]] - transform.pad_top) / transform.scale_y
    result[:, [0, 2]] = np.clip(result[:, [0, 2]], 0, original_w)
    result[:, [1, 3]] = np.clip(result[:, [1, 3]], 0, original_h)
    return result


if __name__ == "__main__":
    # 原图 720x1280，模型输入 640x640；框坐标来自模型输入空间。
    prediction = np.array([[100, 200, 500, 450]], dtype=float)
    print(restore_letterbox_boxes(prediction, original_shape=(720, 1280), input_shape=(640, 640)))
