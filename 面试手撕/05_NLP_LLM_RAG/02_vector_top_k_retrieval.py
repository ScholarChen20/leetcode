"""基于 Embedding 的数值稳定向量检索 Top-K 实现。"""

from __future__ import annotations

from dataclasses import dataclass
import numbers

import numpy as np


@dataclass(frozen=True)
class RetrievalResult:
    """单个召回结果。"""

    index: int
    score: float


def _normalize_vector(values: np.ndarray, name: str) -> np.ndarray:
    """稳定归一化一维向量。"""
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} 必须是非空且仅含有限数值的一维向量。")
    scale = float(np.max(np.abs(vector)))
    if scale == 0:
        raise ValueError(f"{name} 不能是零向量。")
    scaled = vector / scale
    norm = float(np.sqrt(np.dot(scaled, scaled)))
    if not np.isfinite(norm) or norm == 0:
        raise ValueError(f"{name} 无法稳定归一化。")
    return scaled / norm


def _normalize_rows(values: np.ndarray) -> np.ndarray:
    """稳定归一化文档矩阵的每一行。"""
    matrix = np.asarray(values, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0 or not np.all(np.isfinite(matrix)):
        raise ValueError("documents 必须是非空且仅含有限数值的二维数组。")
    scales = np.max(np.abs(matrix), axis=1, keepdims=True)
    if np.any(scales == 0):
        raise ValueError("documents 不能包含零向量。")
    scaled = matrix / scales
    norms = np.sqrt(np.sum(scaled * scaled, axis=1, keepdims=True))
    if np.any(~np.isfinite(norms)) or np.any(norms == 0):
        raise ValueError("documents 无法稳定归一化。")
    return scaled / norms


def vector_top_k_retrieval(
    query_embedding: np.ndarray,
    document_embeddings: np.ndarray,
    top_k: int = 5,
) -> list[RetrievalResult]:
    """按余弦相似度返回最相关的 Top-K 文档下标。

    同分文档按原始下标升序排序，保证结果确定。
    """
    query = _normalize_vector(query_embedding, "query")
    documents = _normalize_rows(document_embeddings)
    if query.shape[0] != documents.shape[1]:
        raise ValueError("query 和 documents 必须具有相同特征维度。")
    if not isinstance(top_k, numbers.Integral) or isinstance(top_k, bool) or not 1 <= top_k <= len(documents):
        raise ValueError("top_k 必须是 [1, 文档数] 区间内的整数。")

    scores = documents @ query
    if not np.all(np.isfinite(scores)):
        raise ValueError("相似度计算溢出。")
    scores = np.clip(scores, -1.0, 1.0)
    ordered = np.lexsort((np.arange(len(scores)), -scores))[: int(top_k)]
    return [RetrievalResult(index=int(index), score=float(scores[index])) for index in ordered]


if __name__ == "__main__":
    query = np.array([1.0, 0.0])
    docs = np.array([[1.0, 0.0], [0.7, 0.7], [0.0, 1.0], [-1.0, 0.0]])
    print(vector_top_k_retrieval(query, docs, top_k=3))
