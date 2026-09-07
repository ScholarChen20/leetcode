"""Adam 优化器的 NumPy 实现。"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
import math

import numpy as np


class Adam:
    """维护一阶、二阶矩估计的 Adam 优化器。"""

    def __init__(
        self,
        learning_rate: float = 1e-3,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ) -> None:
        try:
            values = tuple(float(value) for value in (learning_rate, beta1, beta2, eps))
        except (TypeError, ValueError) as error:
            raise ValueError("Adam 超参数必须是数值。") from error
        learning_rate_value, beta1_value, beta2_value, eps_value = values
        if (
            not all(math.isfinite(value) for value in values)
            or learning_rate_value <= 0
            or not 0 <= beta1_value < 1
            or not 0 <= beta2_value < 1
            or eps_value <= 0
        ):
            raise ValueError("Adam 超参数必须为合法有限数值。")
        self.learning_rate = learning_rate_value
        self.beta1 = beta1_value
        self.beta2 = beta2_value
        self.eps = eps_value
        self.step_count = 0
        self.first_moment: dict[str, np.ndarray] = {}
        self.second_moment: dict[str, np.ndarray] = {}

    def step(self, parameters: MutableMapping[str, np.ndarray], gradients: Mapping[str, np.ndarray]) -> None:
        """根据梯度原地更新 parameters。

        所有参数均先校验并计算临时结果；任一参数不合法、溢出或精度降级后非有限时，
        不修改任何参数或优化器状态。
        """
        if not parameters or parameters.keys() != gradients.keys():
            raise ValueError("参数和梯度必须非空且键完全一致。")

        validated: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
        for name, parameter in parameters.items():
            if not isinstance(parameter, np.ndarray) or not np.issubdtype(parameter.dtype, np.floating):
                raise ValueError(f"参数 {name} 必须是可写浮点 NumPy 数组。")
            if not parameter.flags.writeable or not np.all(np.isfinite(parameter)):
                raise ValueError(f"参数 {name} 必须可写且不含 NaN/Inf。")
            gradient = np.asarray(gradients[name], dtype=np.float64)
            if parameter.shape != gradient.shape or not np.all(np.isfinite(gradient)):
                raise ValueError(f"参数 {name} 与梯度必须形状一致且梯度不含 NaN/Inf。")
            previous_m = self.first_moment.get(name, np.zeros_like(parameter, dtype=np.float64))
            previous_v = self.second_moment.get(name, np.zeros_like(parameter, dtype=np.float64))
            if (
                previous_m.shape != parameter.shape
                or previous_v.shape != parameter.shape
                or not np.all(np.isfinite(previous_m))
                or not np.all(np.isfinite(previous_v))
            ):
                raise ValueError(f"参数 {name} 的历史优化器状态不合法。")
            validated[name] = (parameter, gradient, previous_m, previous_v)

        next_step = self.step_count + 1
        next_moments: dict[str, np.ndarray] = {}
        next_variances: dict[str, np.ndarray] = {}
        updated_parameters: dict[str, np.ndarray] = {}
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            for name, (parameter, gradient, previous_m, previous_v) in validated.items():
                next_m = self.beta1 * previous_m + (1 - self.beta1) * gradient
                next_v = self.beta2 * previous_v + (1 - self.beta2) * gradient**2
                corrected_m = next_m / (1 - self.beta1**next_step)
                corrected_v = next_v / (1 - self.beta2**next_step)
                updated_float64 = parameter.astype(np.float64, copy=False) - self.learning_rate * corrected_m / (
                    np.sqrt(corrected_v) + self.eps
                )
                updated_target_dtype = updated_float64.astype(parameter.dtype, copy=False)
                if (
                    not np.all(np.isfinite(next_m))
                    or not np.all(np.isfinite(next_v))
                    or not np.all(np.isfinite(updated_float64))
                    or not np.all(np.isfinite(updated_target_dtype))
                ):
                    raise ValueError(f"参数 {name} 更新会产生 NaN/Inf，已拒绝提交。")
                next_moments[name] = next_m
                next_variances[name] = next_v
                updated_parameters[name] = updated_target_dtype

        for name, updated in updated_parameters.items():
            parameters[name][...] = updated
        self.first_moment.update(next_moments)
        self.second_moment.update(next_variances)
        self.step_count = next_step


if __name__ == "__main__":
    params = {"weight": np.array([2.0, -3.0])}
    optimizer = Adam(learning_rate=0.1)
    for _ in range(5):
        grads = {"weight": 2 * params["weight"]}  # 最小化 x^2+y^2
        optimizer.step(params, grads)
    print("更新后的参数:", params)
