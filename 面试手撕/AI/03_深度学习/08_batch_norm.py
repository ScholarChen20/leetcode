"""Batch Normalization 前向计算实现。"""

from __future__ import annotations

import math
import numbers

import numpy as np


def _parse_finite_float(value: object, name: str, *, positive: bool = False) -> float:
    """解析有限浮点数并给出统一的业务异常。"""
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} 必须是数值。") from error
    if not math.isfinite(parsed) or (positive and parsed <= 0):
        raise ValueError(f"{name} 必须是{'正的' if positive else '有限的'}有限数值。")
    return parsed


def _stable_channel_statistics(inputs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """使用逐样本 Welford 算法计算通道均值/方差，溢出时明确拒绝。"""
    channels = inputs.shape[1]
    samples = np.moveaxis(inputs, 1, -1).reshape(-1, channels)
    mean = np.zeros(channels, dtype=np.float64)
    m2 = np.zeros(channels, dtype=np.float64)
    count = 0
    with np.errstate(over="ignore", invalid="ignore"):
        for sample in samples:
            count += 1
            delta = sample - mean
            mean += delta / count
            delta_after_mean = sample - mean
            m2 += delta * delta_after_mean
    variance = m2 / count
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(variance)) or np.any(variance < 0):
        raise ValueError("输入数值范围导致均值或方差溢出。")
    return mean, variance


class BatchNorm:
    """支持 [N, C] 和 [N, C, H, W] 输入的 BatchNorm。"""

    def __init__(self, num_features: int, momentum: float = 0.1, eps: float = 1e-5) -> None:
        momentum_value = _parse_finite_float(momentum, "momentum")
        eps_value = _parse_finite_float(eps, "eps", positive=True)
        if (
            not isinstance(num_features, numbers.Integral)
            or isinstance(num_features, bool)
            or num_features <= 0
            or not 0 < momentum_value <= 1
        ):
            raise ValueError("num_features 必须为正整数，momentum 必须在 (0, 1]。")
        self.num_features = int(num_features)
        self.momentum = momentum_value
        self.eps = eps_value
        self.gamma = np.ones(self.num_features, dtype=np.float64)
        self.beta = np.zeros(self.num_features, dtype=np.float64)
        self.running_mean = np.zeros(self.num_features, dtype=np.float64)
        self.running_var = np.ones(self.num_features, dtype=np.float64)

    def forward(self, inputs: np.ndarray, training: bool = True) -> np.ndarray:
        """执行训练或推理阶段的 BatchNorm 前向计算。"""
        x = np.asarray(inputs, dtype=np.float64)
        if x.ndim not in (2, 4) or x.shape[1] != self.num_features:
            raise ValueError("输入必须是 [N,C] 或 [N,C,H,W]，且 C 等于 num_features。")
        axes = (0,) if x.ndim == 2 else (0, 2, 3)
        reduction_count = int(np.prod([x.shape[axis] for axis in axes]))
        if reduction_count == 0:
            raise ValueError("BatchNorm 不接受空 batch 或空空间维度。")
        if not np.all(np.isfinite(x)):
            raise ValueError("inputs 不能包含 NaN 或 Inf。")
        if (
            not all(np.all(np.isfinite(values)) for values in (self.gamma, self.beta, self.running_mean, self.running_var))
            or np.any(self.running_var < 0)
        ):
            raise ValueError("BatchNorm 参数和运行统计量必须有限，且 running_var 不能为负数。")

        broadcast_shape = (1, self.num_features) if x.ndim == 2 else (1, self.num_features, 1, 1)
        if training:
            mean, variance = _stable_channel_statistics(x)
            next_running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            next_running_var = (1 - self.momentum) * self.running_var + self.momentum * variance
        else:
            mean = self.running_mean
            variance = self.running_var
            next_running_mean = self.running_mean
            next_running_var = self.running_var

        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            normalized = (x - mean.reshape(broadcast_shape)) / np.sqrt(variance.reshape(broadcast_shape) + self.eps)
            output = normalized * self.gamma.reshape(broadcast_shape) + self.beta.reshape(broadcast_shape)
        if (
            not np.all(np.isfinite(next_running_mean))
            or not np.all(np.isfinite(next_running_var))
            or np.any(next_running_var < 0)
            or not np.all(np.isfinite(output))
        ):
            raise ValueError("BatchNorm 计算产生 NaN/Inf 或负方差，运行统计量未提交。")
        if training:
            self.running_mean = next_running_mean
            self.running_var = next_running_var
        return output


if __name__ == "__main__":
    layer = BatchNorm(num_features=2)
    batch = np.array([[1.0, 10.0], [3.0, 14.0], [5.0, 18.0]])
    print("训练输出:\n", layer.forward(batch, training=True))
    print("推理输出:\n", layer.forward(batch, training=False))
