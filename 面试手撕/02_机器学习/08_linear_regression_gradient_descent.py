"""使用批量梯度下降实现线性回归。"""

from __future__ import annotations

import math
import numbers

import numpy as np


class LinearRegressionGD:
    """最小化均方误差的线性回归模型。"""

    def __init__(self, learning_rate: float = 0.01, epochs: int = 1_000) -> None:
        if (
            not math.isfinite(float(learning_rate))
            or learning_rate <= 0
            or not isinstance(epochs, numbers.Integral)
            or isinstance(epochs, bool)
            or epochs <= 0
        ):
            raise ValueError("learning_rate 必须为有限正数，epochs 必须为正整数。")
        self.learning_rate = float(learning_rate)
        self.epochs = int(epochs)
        self.weights: np.ndarray | None = None
        self.bias = 0.0
        self.loss_history: list[float] = []

    @staticmethod
    def _validate_features(features: np.ndarray, expected_features: int | None = None) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] == 0 or not np.all(np.isfinite(x)):
            raise ValueError("features 必须是非空且仅含有限数值的二维数组。")
        if expected_features is not None and x.shape[1] != expected_features:
            raise ValueError("features 的特征维度与训练时不一致。")
        return x

    def fit(self, features: np.ndarray, targets: np.ndarray) -> "LinearRegressionGD":
        x = self._validate_features(features)
        y = np.asarray(targets, dtype=np.float64)
        if y.shape != (x.shape[0],) or not np.all(np.isfinite(y)):
            raise ValueError("targets 必须与样本数一致且仅含有限数值。")

        sample_count, feature_count = x.shape
        self.weights = np.zeros(feature_count, dtype=np.float64)
        self.bias = 0.0
        self.loss_history.clear()
        for _ in range(self.epochs):
            predictions = x @ self.weights + self.bias
            error = predictions - y
            self.weights -= self.learning_rate * (2.0 / sample_count) * (x.T @ error)
            self.bias -= self.learning_rate * 2.0 * float(error.mean())
            self.loss_history.append(float(np.mean(error**2)))
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("模型尚未训练。")
        x = self._validate_features(features, expected_features=self.weights.shape[0])
        return x @ self.weights + self.bias


if __name__ == "__main__":
    x_train = np.array([[1], [2], [3], [4], [5]], dtype=float)
    y_train = np.array([3, 5, 7, 9, 11], dtype=float)
    model = LinearRegressionGD(learning_rate=0.03, epochs=2_000).fit(x_train, y_train)
    print("权重:", model.weights, "偏置:", model.bias)
    print("预测 x=6:", model.predict(np.array([[6.0]])))
