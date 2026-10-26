"""线程安全、单一时间域的令牌桶限流器实现。"""

from __future__ import annotations

from collections.abc import Callable
import math
import threading
import time


Clock = Callable[[], float]


class TokenBucketRateLimiter:
    """以固定速率补充令牌的限流器。

    构造时注入单一单调时钟；生产调用不暴露任意 ``now``，避免把 epoch 时间和
    monotonic 时间混用导致桶永久冻结或重复补充。
    """

    def __init__(self, capacity: float, refill_rate_per_second: float, clock: Clock = time.monotonic) -> None:
        try:
            capacity_value = float(capacity)
            refill_rate = float(refill_rate_per_second)
        except (TypeError, ValueError) as error:
            raise ValueError("capacity 和 refill_rate_per_second 必须是数值。") from error
        if (
            not callable(clock)
            or not math.isfinite(capacity_value)
            or not math.isfinite(refill_rate)
            or capacity_value <= 0
            or refill_rate <= 0
        ):
            raise ValueError("clock 必须可调用，capacity 和 refill_rate_per_second 必须为有限正数。")
        self.capacity = capacity_value
        self.refill_rate_per_second = refill_rate
        self._clock = clock
        self._tokens = self.capacity
        self._last_refill = self._now()
        self._lock = threading.Lock()

    def _now(self) -> float:
        current_time = float(self._clock())
        if not math.isfinite(current_time):
            raise ValueError("clock 必须返回有限单调时间。")
        return current_time

    def _refill_locked(self, current_time: float) -> None:
        """在锁内补充令牌；时钟回退时不重复补充。"""
        effective_time = max(current_time, self._last_refill)
        elapsed = effective_time - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate_per_second)
        self._last_refill = effective_time

    def try_acquire(self, requested_tokens: float = 1.0) -> bool:
        """尝试获取令牌；令牌不足时返回 False。"""
        try:
            requested = float(requested_tokens)
        except (TypeError, ValueError) as error:
            raise ValueError("requested_tokens 必须是数值。") from error
        if not math.isfinite(requested) or not 0 < requested <= self.capacity:
            raise ValueError("requested_tokens 必须在 (0, capacity] 范围内且为有限数。")
        with self._lock:
            self._refill_locked(self._now())
            if self._tokens < requested:
                return False
            self._tokens -= requested
            return True

    @property
    def available_tokens(self) -> float:
        """返回补充到当前时刻后的可用令牌数。"""
        with self._lock:
            self._refill_locked(self._now())
            return self._tokens


if __name__ == "__main__":
    fake_now = [0.0]
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_second=1, clock=lambda: fake_now[0])
    print([limiter.try_acquire() for _ in range(3)])
    fake_now[0] += 1.0
    print("1 秒后:", limiter.try_acquire())
