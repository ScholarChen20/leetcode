"""K-Means 聚类的 NumPy 实现。"""

from __future__ import annotations

import math
import numbers

import numpy as np


class KMeans:
    """使用欧氏距离和随机初始化的 K-Means。"""

    def __init__(self, n_clusters: int, max_iter: int = 300, tolerance: float = 1e-4, random_state: int | None = None) -> None:
        if (
            not isinstance(n_clusters, numbers.Integral)
            or isinstance(n_clusters, bool)
            or not isinstance(max_iter, numbers.Integral)
            or isinstance(max_iter, bool)
            or n_clusters <= 0
            or max_iter <= 0
            or not math.isfinite(float(tolerance))
            or tolerance < 0
        ):
            raise ValueError("n_clusters/max_iter 必须为正整数，tolerance 必须为非负有限数。")
        self.n_clusters = int(n_clusters)
        self.max_iter = int(max_iter)
        self.tolerance = float(tolerance)
        self.random_state = random_state
        self.cluster_centers_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None

    @staticmethod
    def _validate_features(features: np.ndarray, expected_dimension: int | None = None) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] == 0 or not np.all(np.isfinite(x)):
            raise ValueError("features 必须是非空且仅含有限数值的二维数组。")
        if expected_dimension is not None and x.shape[1] != expected_dimension:
            raise ValueError("features 的特征维度与聚类中心不一致。")
        return x

    def fit(self, features: np.ndarray) -> "KMeans":
        x = self._validate_features(features)
        if x.shape[0] < self.n_clusters:
            raise ValueError("样本数必须不少于聚类数量。")

        rng = np.random.default_rng(self.random_state)
        centers = x[rng.choice(x.shape[0], self.n_clusters, replace=False)].copy()

        for _ in range(self.max_iter):
            distances = np.linalg.norm(x[:, None, :] - centers[None, :, :], axis=2)
            labels = distances.argmin(axis=1)
            next_centers = centers.copy()
            for cluster_index in range(self.n_clusters):
                members = x[labels == cluster_index]
                if len(members) > 0:
                    next_centers[cluster_index] = members.mean(axis=0)

            if np.linalg.norm(next_centers - centers) <= self.tolerance:
                centers = next_centers
                break
            centers = next_centers

        self.cluster_centers_ = centers
        self.labels_ = self.predict(x)
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self.cluster_centers_ is None:
            raise RuntimeError("模型尚未训练。")
        x = self._validate_features(features, expected_dimension=self.cluster_centers_.shape[1])
        distances = np.linalg.norm(x[:, None, :] - self.cluster_centers_[None, :, :], axis=2)
        return distances.argmin(axis=1)


if __name__ == "__main__":
    points = np.array([[1, 1], [1.2, 0.8], [0.8, 1.1], [8, 8], [8.3, 7.8], [7.8, 8.2]])
    model = KMeans(n_clusters=2, random_state=42).fit(points)
    print("聚类中心:\n", model.cluster_centers_)
    print("样本标签:", model.labels_)
