"""教学版 Byte Pair Encoding（BPE）Tokenizer 实现。"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
import numbers


class BPETokenizer:
    """在词级语料上学习合并规则的简化 BPE。"""

    def __init__(self) -> None:
        self.merges: list[tuple[str, str]] = []

    @staticmethod
    def _merge_pair(symbols: tuple[str, ...], pair: tuple[str, str]) -> tuple[str, ...]:
        merged: list[str] = []
        index = 0
        while index < len(symbols):
            if index < len(symbols) - 1 and (symbols[index], symbols[index + 1]) == pair:
                merged.append(symbols[index] + symbols[index + 1])
                index += 2
            else:
                merged.append(symbols[index])
                index += 1
        return tuple(merged)

    def fit(self, corpus: Sequence[str], num_merges: int = 20) -> "BPETokenizer":
        """从语料学习出现频率最高的相邻 token 合并规则。"""
        if not isinstance(num_merges, numbers.Integral) or isinstance(num_merges, bool) or num_merges < 0:
            raise ValueError("num_merges 必须是非负整数。")
        vocabulary: Counter[tuple[str, ...]] = Counter()
        for sentence in corpus:
            if not isinstance(sentence, str):
                raise ValueError("corpus 中的每个元素必须是字符串。")
            for word in sentence.split():
                vocabulary[tuple(word) + ("</w>",)] += 1
        if not vocabulary:
            raise ValueError("语料中至少需要一个非空词。")

        self.merges.clear()
        for _ in range(int(num_merges)):
            pair_counts: Counter[tuple[str, str]] = Counter()
            for symbols, frequency in vocabulary.items():
                for index in range(len(symbols) - 1):
                    pair_counts[(symbols[index], symbols[index + 1])] += frequency
            if not pair_counts:
                break
            best_pair = min(pair_counts, key=lambda pair: (-pair_counts[pair], pair))
            merged_vocabulary: Counter[tuple[str, ...]] = Counter()
            for symbols, frequency in vocabulary.items():
                merged_vocabulary[self._merge_pair(symbols, best_pair)] += frequency
            vocabulary = merged_vocabulary
            self.merges.append(best_pair)
        return self

    def encode_word(self, word: str) -> list[str]:
        """按学习到的合并规则编码一个词。"""
        if not isinstance(word, str):
            raise ValueError("word 必须是字符串。")
        if not word:
            return []
        symbols = tuple(word) + ("</w>",)
        for pair in self.merges:
            symbols = self._merge_pair(symbols, pair)
        return list(symbols)

    def encode(self, text: str) -> list[str]:
        """编码整句文本。"""
        if not isinstance(text, str):
            raise ValueError("text 必须是字符串。")
        return [token for word in text.split() for token in self.encode_word(word)]


if __name__ == "__main__":
    tokenizer = BPETokenizer().fit(["low lower newest widest", "lower lowest"], num_merges=10)
    print("合并规则:", tokenizer.merges)
    print("编码结果:", tokenizer.encode("lower newest"))
