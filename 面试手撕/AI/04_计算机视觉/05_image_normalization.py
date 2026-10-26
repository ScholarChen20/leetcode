"""图像归一化、标准化及反标准化实现。"""

from __future__ import annotations

import numpy as np


def _validate_hwc_image(image: np.ndarray, name: str) -> np.ndarray:
    """转换并验证有限 HWC 图像。"""
    values = np.asarray(image, dtype=np.float64)
    if values.ndim != 3 or values.shape[-1] == 0 or not np.all(np.isfinite(values)):
        raise ValueError(f"{name} 必须是仅含有限数值的 HWC 图像。")
    return values


def _validate_channel_statistics(mean: np.ndarray, std: np.ndarray, channels: int) -> tuple[np.ndarray, np.ndarray]:
    """验证每通道均值和正标准差。"""
    channel_mean = np.asarray(mean, dtype=np.float64)
    channel_std = np.asarray(std, dtype=np.float64)
    if (
        channel_mean.shape != (channels,)
        or channel_std.shape != (channels,)
        or not np.all(np.isfinite(channel_mean))
        or not np.all(np.isfinite(channel_std))
        or np.any(channel_std <= 0)
    ):
        raise ValueError("mean/std 必须与通道数一致、有限，且 std 必须大于 0。")
    return channel_mean, channel_std


def normalize_to_unit_interval(image: np.ndarray) -> np.ndarray:
    """将 [0, 255] 像素值缩放到 [0, 1]，越界输入会被拒绝。"""
    values = np.asarray(image, dtype=np.float64)
    if not np.all(np.isfinite(values)) or np.any(values < 0) or np.any(values > 255):
        raise ValueError("image 必须仅包含 [0, 255] 内的有限像素值。")
    return values / 255.0


def standardize_image(image: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """按通道标准化 HWC 图像。"""
    x = _validate_hwc_image(image, "image")
    channel_mean, channel_std = _validate_channel_statistics(mean, std, x.shape[-1])
    return (x - channel_mean) / channel_std


def destandardize_image(image: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """还原按通道标准化后的 HWC 图像。"""
    x = _validate_hwc_image(image, "image")
    channel_mean, channel_std = _validate_channel_statistics(mean, std, x.shape[-1])
    return x * channel_std + channel_mean


if __name__ == "__main__":
    rgb = np.array([[[0, 128, 255]]], dtype=np.uint8)
    scaled = normalize_to_unit_interval(rgb)
    normalized = standardize_image(scaled, np.array([0.5, 0.5, 0.5]), np.array([0.5, 0.5, 0.5]))
    print("归一化:", scaled)
    print("标准化:", normalized)
