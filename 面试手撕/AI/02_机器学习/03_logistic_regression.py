"""使用批量梯度下降实现二分类逻辑回归。"""

from __future__ import annotations

import math
import numbers

import numpy as np


class LogisticRegressionGD:
    """不依赖 sklearn 的二分类逻辑回归。"""

    def __init__(self, learning_rate: float = 0.1, epochs: int = 1_000) -> None:
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
    def _sigmoid(values: np.ndarray) -> np.ndarray:
        clipped = np.clip(values, -500, 500)
        return 1.0 / (1.0 + np.exp(-clipped))

    @staticmethod
    def _validate_features(features: np.ndarray, expected_features: int | None = None) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] == 0 or not np.all(np.isfinite(x)):
            raise ValueError("features 必须是非空且仅含有限数值的二维数组。")
        if expected_features is not None and x.shape[1] != expected_features:
            raise ValueError("features 的特征维度与训练时不一致。")
        return x

    def fit(self, features: np.ndarray, labels: np.ndarray) -> "LogisticRegressionGD":
        x = self._validate_features(features)
        y = np.asarray(labels, dtype=np.float64)
        if y.shape != (x.shape[0],) or not np.all(np.isfinite(y)) or not np.all(np.isin(y, [0.0, 1.0])):
            raise ValueError("labels 必须与样本数一致且只包含 0 或 1。")

        sample_count, feature_count = x.shape
        self.weights = np.zeros(feature_count, dtype=np.float64)
        self.bias = 0.0
        self.loss_history.clear()

        for _ in range(self.epochs):
            logits = x @ self.weights + self.bias
            probabilities = self._sigmoid(logits)
            error = probabilities - y
            gradient_weights = x.T @ error / sample_count
            gradient_bias = float(error.mean())
            self.weights -= self.learning_rate * gradient_weights
            self.bias -= self.learning_rate * gradient_bias

            probabilities = np.clip(probabilities, 1e-12, 1.0 - 1e-12)
            loss = -np.mean(y * np.log(probabilities) + (1 - y) * np.log(1 - probabilities))
            self.loss_history.append(float(loss))
        return self

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("模型尚未训练。")
        x = self._validate_features(features, expected_features=self.weights.shape[0])
        return self._sigmoid(x @ self.weights + self.bias)

    def predict(self, features: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        if not math.isfinite(float(threshold)) or not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold 必须是 [0, 1] 内的有限数值。")
        return (self.predict_proba(features) >= threshold).astype(np.int64)


if __name__ == "__main__":
    x_train = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y_train = np.array([0, 0, 0, 1])
    model = LogisticRegressionGD(learning_rate=0.5, epochs=2_000).fit(x_train, y_train)
    print("预测概率:", model.predict_proba(x_train))
    print("预测标签:", model.predict(x_train))
    print("最终损失:", model.loss_history[-1])
