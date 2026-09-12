"""仅面向稳定幂等键操作的指数退避重试实现。"""

from __future__ import annotations

from collections.abc import Callable
import math
import numbers
import time
from typing import TypeVar


T = TypeVar("T")


def retry_with_backoff(
    operation: Callable[[str], T],
    *,
    idempotency_key: str,
    max_attempts: int = 3,
    base_delay_seconds: float = 0.1,
    max_delay_seconds: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (TimeoutError, ConnectionError),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """使用同一稳定幂等键对可重放操作执行有限次数指数退避。

    ``operation`` 必须把 ``idempotency_key`` 传给下游服务；没有稳定键的写操作
    不得使用本函数。网络超时并不代表下游未执行，因此重试安全性取决于下游幂等契约。
    """
    if not callable(operation) or not callable(sleep) or not isinstance(idempotency_key, str) or not idempotency_key:
        raise ValueError("operation/sleep 必须可调用，idempotency_key 必须为非空字符串。")
    if (
        not isinstance(max_attempts, numbers.Integral)
        or isinstance(max_attempts, bool)
        or max_attempts <= 0
    ):
        raise ValueError("max_attempts 必须为正整数。")
    try:
        base_delay = float(base_delay_seconds)
        max_delay = float(max_delay_seconds)
    except (TypeError, ValueError) as error:
        raise ValueError("重试延迟必须是数值。") from error
    if not math.isfinite(base_delay) or not math.isfinite(max_delay) or base_delay < 0 or max_delay < 0:
        raise ValueError("重试延迟必须为非负有限数。")
    if not retryable_exceptions or not all(isinstance(exception_type, type) and issubclass(exception_type, Exception) for exception_type in retryable_exceptions):
        raise ValueError("retryable_exceptions 必须是非空异常类型元组。")

    for attempt in range(int(max_attempts)):
        try:
            return operation(idempotency_key)
        except retryable_exceptions:
            if attempt == max_attempts - 1:
                raise
            delay = min(base_delay * (2**attempt), max_delay)
            sleep(delay)
    raise RuntimeError("不可达代码。")


if __name__ == "__main__":
    attempts = [0]

    def flaky_read_operation(key: str) -> str:
        assert key == "read:example-001"
        attempts[0] += 1
        if attempts[0] < 3:
            raise TimeoutError("临时网络抖动")
        return "成功"

    print(
        retry_with_backoff(
            flaky_read_operation,
            idempotency_key="read:example-001",
            sleep=lambda _: None,
        )
    )
