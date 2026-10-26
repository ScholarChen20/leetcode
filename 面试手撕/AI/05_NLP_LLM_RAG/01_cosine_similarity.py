"""文本 Embedding 常用的数值稳定余弦相似度实现。"""

from __future__ import annotations

import numpy as np


def _normalize_vector(values: np.ndarray, name: str) -> np.ndarray:
    """用最大绝对值缩放后归一化，避免有限大向量求范数时溢出。"""
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size == 0 or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} 必须是非空且仅含有限数值的一维向量。")
    scale = float(np.max(np.abs(vector)))
    if scale == 0:
        raise ValueError(f"{name} 不能是零向量。")
    scaled = vector / scale
    norm = float(np.sqrt(np.dot(scaled, scaled)))
    if not math_is_finite_positive(norm):
        raise ValueError(f"{name} 无法稳定归一化。")
    normalized = scaled / norm
    if not np.all(np.isfinite(normalized)):
        raise ValueError(f"{name} 无法稳定归一化。")
    return normalized


def math_is_finite_positive(value: float) -> bool:
    """判断归一化中间量是否是有限正数。"""
    return bool(np.isfinite(value) and value > 0)


def _normalize_matrix(values: np.ndarray, name: str) -> np.ndarray:
    """按行稳定 L2 归一化二维向量矩阵。"""
    matrix = np.asarray(values, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0 or not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} 必须是非空且仅含有限数值的二维数组。")
    scales = np.max(np.abs(matrix), axis=1, keepdims=True)
    if np.any(scales == 0):
        raise ValueError(f"{name} 中不能包含零向量。")
    scaled = matrix / scales
    norms = np.sqrt(np.sum(scaled * scaled, axis=1, keepdims=True))
    if np.any(~np.isfinite(norms)) or np.any(norms == 0):
        raise ValueError(f"{name} 无法稳定归一化。")
    normalized = scaled / norms
    if not np.all(np.isfinite(normalized)):
        raise ValueError(f"{name} 无法稳定归一化。")
    return normalized


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """计算两个一维向量的余弦相似度。"""
    a = _normalize_vector(vector_a, "vector_a")
    b = _normalize_vector(vector_b, "vector_b")
    if a.shape != b.shape:
        raise ValueError("两个向量必须维度相同。")
    score = float(np.dot(a, b))
    if not np.isfinite(score):
        raise ValueError("余弦相似度计算溢出。")
    return float(np.clip(score, -1.0, 1.0))


def cosine_similarity_matrix(queries: np.ndarray, documents: np.ndarray) -> np.ndarray:
    """计算查询向量与文档向量之间的两两余弦相似度。"""
    query_vectors = _normalize_matrix(queries, "queries")
    document_vectors = _normalize_matrix(documents, "documents")
    if query_vectors.shape[1] != document_vectors.shape[1]:
        raise ValueError("queries/documents 必须具有相同特征维度。")
    scores = query_vectors @ document_vectors.T
    if not np.all(np.isfinite(scores)):
        raise ValueError("余弦相似度矩阵计算溢出。")
    return np.clip(scores, -1.0, 1.0)


if __name__ == "__main__":
    query = np.array([1.0, 2.0, 3.0])
    document = np.array([2.0, 4.0, 6.0])
    print("余弦相似度:", cosine_similarity(query, document))
