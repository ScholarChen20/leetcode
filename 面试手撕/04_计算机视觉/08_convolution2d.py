"""二维单通道卷积实现。"""

from __future__ import annotations

import numbers

import numpy as np


def conv2d(
    image: np.ndarray,
    kernel: np.ndarray,
    stride: int = 1,
    padding: int = 0,
) -> np.ndarray:
    """执行 CNN 中常用的互相关计算（不翻转卷积核）。"""
    source = np.asarray(image, dtype=np.float64)
    filter_kernel = np.asarray(kernel, dtype=np.float64)
    if (
        source.ndim != 2
        or filter_kernel.ndim != 2
        or source.size == 0
        or filter_kernel.size == 0
        or not np.all(np.isfinite(source))
        or not np.all(np.isfinite(filter_kernel))
    ):
        raise ValueError("image 和 kernel 必须是非空且仅含有限数值的二维数组。")
    if (
        not isinstance(stride, numbers.Integral)
        or isinstance(stride, bool)
        or not isinstance(padding, numbers.Integral)
        or isinstance(padding, bool)
        or stride <= 0
        or padding < 0
    ):
        raise ValueError("stride 必须为正整数，padding 必须为非负整数。")

    stride, padding = int(stride), int(padding)
    padded = np.pad(source, ((padding, padding), (padding, padding)), mode="constant")
    kernel_h, kernel_w = filter_kernel.shape
    output_h = (padded.shape[0] - kernel_h) // stride + 1
    output_w = (padded.shape[1] - kernel_w) // stride + 1
    if output_h <= 0 or output_w <= 0:
        raise ValueError("卷积核尺寸不能大于有效输入尺寸。")

    output = np.empty((output_h, output_w), dtype=np.float64)
    for row in range(output_h):
        for col in range(output_w):
            patch = padded[row * stride : row * stride + kernel_h, col * stride : col * stride + kernel_w]
            output[row, col] = np.sum(patch * filter_kernel)
    return output


if __name__ == "__main__":
    image = np.arange(1, 10).reshape(3, 3)
    edge_kernel = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
    print(conv2d(image, edge_kernel, padding=1))
