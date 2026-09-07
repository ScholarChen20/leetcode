"""BM25 文本检索实现。"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import math


class BM25:
    """基于已分词文档的 BM25 检索器。"""

    def __init__(self, tokenized_documents: Sequence[Sequence[str]], k1: float = 1.5, b: float = 0.75) -> None:
        if not tokenized_documents or k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("文档不能为空，k1 必须为正数，b 必须在 [0,1]。")
        self.documents = [list(document) for document in tokenized_documents]
        self.k1 = k1
        self.b = b
        self.document_lengths = [len(document) for document in self.documents]
        self.average_length = sum(self.document_lengths) / len(self.document_lengths)
        self.term_frequencies = [Counter(document) for document in self.documents]
        document_frequency: Counter[str] = Counter()
        for document in self.documents:
            document_frequency.update(set(document))
        total_documents = len(self.documents)
        self.idf = {
            term: math.log(1 + (total_documents - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def score(self, query_tokens: Sequence[str], document_index: int) -> float:
        """计算一个查询与指定文档的 BM25 分数。"""
        if not 0 <= document_index < len(self.documents):
            raise IndexError("document_index 越界。")
        frequencies = self.term_frequencies[document_index]
        document_length = self.document_lengths[document_index]
        score = 0.0
        for term in query_tokens:
            term_frequency = frequencies.get(term, 0)
            if term_frequency == 0:
                continue
            numerator = term_frequency * (self.k1 + 1)
            denominator = term_frequency + self.k1 * (1 - self.b + self.b * document_length / self.average_length)
            score += self.idf.get(term, 0.0) * numerator / denominator
        return score

    def search(self, query_tokens: Sequence[str], top_k: int = 5) -> list[tuple[int, float]]:
        """返回按 BM25 分数降序的 Top-K 文档。"""
        if not 1 <= top_k <= len(self.documents):
            raise ValueError("top_k 必须在 [1, 文档数] 区间。")
        scores = [(index, self.score(query_tokens, index)) for index in range(len(self.documents))]
        return sorted(scores, key=lambda item: item[1], reverse=True)[:top_k]


if __name__ == "__main__":
    corpus = [
        "员工 差旅 费用 报销 流程".split(),
        "员工 年假 申请 规则".split(),
        "差旅 出行 预订 和 费用 管理".split(),
    ]
    retriever = BM25(corpus)
    print(retriever.search("差旅 报销".split(), top_k=2))
