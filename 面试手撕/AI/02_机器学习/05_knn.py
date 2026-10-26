"""KNN 分类器的简单实现。"""

from __future__ import annotations

import numbers

import numpy as np


class KNearestNeighbors:
    """使用欧氏距离和多数投票的 KNN 分类器。"""

    def __init__(self, n_neighbors: int = 3) -> None:
        if not isinstance(n_neighbors, numbers.Integral) or isinstance(n_neighbors, bool) or n_neighbors <= 0:
            raise ValueError("n_neighbors 必须为正整数。")
        self.n_neighbors = int(n_neighbors)
        self._features: np.ndarray | None = None
        self._labels: np.ndarray | None = None

    @staticmethod
    def _validate_features(features: np.ndarray, expected_dimension: int | None = None) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] == 0 or not np.all(np.isfinite(x)):
            raise ValueError("features 必须是非空且仅含有限数值的二维数组。")
        if expected_dimension is not None and x.shape[1] != expected_dimension:
            raise ValueError("待预测特征维度不匹配。")
        return x

    def fit(self, features: np.ndarray, labels: np.ndarray) -> "KNearestNeighbors":
        x = self._validate_features(features)
        y = np.asarray(labels)
        if y.shape != (x.shape[0],):
            raise ValueError("labels 必须是一维且与样本数一致。")
        if self.n_neighbors > x.shape[0]:
            raise ValueError("n_neighbors 不能超过训练样本数。")
        self._features = x
        self._labels = y
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self._features is None or self._labels is None:
            raise RuntimeError("模型尚未训练。")
        x = self._validate_features(features, expected_dimension=self._features.shape[1])

        predictions: list[object] = []
        for sample in x:
            distances = np.linalg.norm(self._features - sample, axis=1)
            nearest_indices = np.argsort(distances, kind="mergesort")[: self.n_neighbors]
            nearest_labels = self._labels[nearest_indices]
            labels, counts = np.unique(nearest_labels, return_counts=True)
            predictions.append(labels[np.argmax(counts)])
        return np.asarray(predictions)


if __name__ == "__main__":
    x_train = np.array([[0, 0], [0, 1], [1, 0], [4, 4], [4, 5], [5, 4]], dtype=float)
    y_train = np.array([0, 0, 0, 1, 1, 1])
    model = KNearestNeighbors(n_neighbors=3).fit(x_train, y_train)
    print(model.predict(np.array([[0.5, 0.4], [4.5, 4.2]])))
