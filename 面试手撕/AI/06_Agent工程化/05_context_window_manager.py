"""按 Token 预算裁剪 Agent 上下文的窗口管理器。"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Sequence
import numbers


@dataclass(frozen=True)
class ChatMessage:
    """最小聊天消息。"""

    role: str
    content: str


TokenCounter = Callable[[str], int]


def approximate_token_count(text: str) -> int:
    """近似估计 Token 数：中文/英文混合场景可用于本地演示，不替代真实 tokenizer。"""
    return max(1, (len(text) + 3) // 4) if text else 0


class ContextWindowManager:
    """在预算内优先保留 System Prompt 和最近消息。"""

    def __init__(self, max_tokens: int, token_counter: TokenCounter = approximate_token_count) -> None:
        if not isinstance(max_tokens, numbers.Integral) or isinstance(max_tokens, bool) or max_tokens <= 0:
            raise ValueError("max_tokens 必须为正整数。")
        self.max_tokens = int(max_tokens)
        self.token_counter = token_counter

    def _count(self, content: str) -> int:
        """校验 Token 计数器返回值。"""
        count = self.token_counter(content)
        if not isinstance(count, numbers.Integral) or isinstance(count, bool) or count < 0:
            raise ValueError("token_counter 必须返回非负整数。")
        return int(count)

    def fit(self, messages: Sequence[ChatMessage]) -> list[ChatMessage]:
        """返回不超过预算的消息；超预算 System Prompt 会被明确拒绝。"""
        values = list(messages)
        if not values:
            return []
        system = values[:1] if values[0].role == "system" else []
        system_tokens = sum(self._count(item.content) for item in system)
        if system_tokens > self.max_tokens:
            raise ValueError("System Prompt 已超过上下文 Token 预算，需先压缩或提高预算。")

        body = values[len(system) :]
        selected: list[ChatMessage] = []
        used = system_tokens
        for message in reversed(body):
            message_tokens = self._count(message.content)
            if used + message_tokens > self.max_tokens:
                break
            selected.append(message)
            used += message_tokens
        selected.reverse()

        omitted_count = len(body) - len(selected)
        result = system.copy()
        if omitted_count > 0:
            summary = ChatMessage("assistant", f"历史压缩提示：已省略 {omitted_count} 条早期消息。")
            summary_tokens = self._count(summary.content)
            if used + summary_tokens <= self.max_tokens:
                result.append(summary)
        result.extend(selected)
        return result


if __name__ == "__main__":
    manager = ContextWindowManager(max_tokens=30)
    messages = [ChatMessage("system", "你是客服助手。")]
    messages.extend(ChatMessage("user", f"这是第 {index} 条历史消息，包含一些上下文。") for index in range(10))
    print(manager.fit(messages))
