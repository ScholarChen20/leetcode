"""并发场景下避免重复执行写操作的幂等键实现。

该实现采用 ``UNKNOWN`` 状态处理超时或异常导致的结果不确定性：未知结果
永不在本 Store 内自动重试；必须以新的业务流程完成外部副作用对账。生产场景
还需把 execution_id 作为 fencing token 传给下游持久化服务。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
import math
import threading
import time
from typing import TypeVar, cast
import uuid


T = TypeVar("T")
Clock = Callable[[], float]


class IdempotencyStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    UNKNOWN = "UNKNOWN"


@dataclass
class IdempotencyRecord:
    """幂等请求的运行状态和结果。"""

    status: IdempotencyStatus
    request_fingerprint: str
    execution_id: str
    created_at: float
    updated_at: float
    result: object | None = None
    error_type: str | None = None


class IdempotencyStore:
    """相同 key 的请求在已知状态下只执行一次。

    对任何异常或过期运行状态，默认转为 ``UNKNOWN`` 而非自动重试；这样不会
    在“下游已成功、客户端未收到响应”的场景产生重复写入。
    """

    def __init__(
        self,
        wait_timeout_seconds: float = 10.0,
        record_ttl_seconds: float = 3_600.0,
        clock: Clock = time.monotonic,
    ) -> None:
        if (
            not callable(clock)
            or not math.isfinite(float(wait_timeout_seconds))
            or not math.isfinite(float(record_ttl_seconds))
            or wait_timeout_seconds <= 0
            or record_ttl_seconds <= 0
        ):
            raise ValueError("clock 必须可调用，等待超时和 TTL 必须为有限正数。")
        self.wait_timeout_seconds = float(wait_timeout_seconds)
        self.record_ttl_seconds = float(record_ttl_seconds)
        self._clock = clock
        self._records: dict[str, IdempotencyRecord] = {}
        self._condition = threading.Condition()

    def _now(self) -> float:
        current_time = float(self._clock())
        if not math.isfinite(current_time):
            raise ValueError("clock 必须返回有限单调时间。")
        return current_time

    def _purge_success_records_locked(self, current_time: float) -> None:
        """仅清理成功且过期的记录，未知结果必须保留以等待人工对账。"""
        expired_keys = [
            key
            for key, record in self._records.items()
            if record.status is IdempotencyStatus.SUCCESS and current_time - record.updated_at >= self.record_ttl_seconds
        ]
        for key in expired_keys:
            del self._records[key]

    @staticmethod
    def _validate_request(key: str, request_fingerprint: str) -> None:
        if not isinstance(key, str) or not key or not isinstance(request_fingerprint, str) or not request_fingerprint:
            raise ValueError("key 和 request_fingerprint 必须为非空字符串。")

    def execute(
        self,
        key: str,
        operation: Callable[[str], T],
        request_fingerprint: str,
        wait_timeout_seconds: float | None = None,
    ) -> T:
        """以唯一 execution_id 执行幂等操作。

        operation 必须将传入的 execution_id 作为下游写操作的 fencing token 或
        幂等键使用。遇到异常时本方法保守地标记 UNKNOWN，禁止自动重试。
        """
        self._validate_request(key, request_fingerprint)
        timeout = self.wait_timeout_seconds if wait_timeout_seconds is None else float(wait_timeout_seconds)
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("wait_timeout_seconds 必须为有限正数。")

        with self._condition:
            current_time = self._now()
            self._purge_success_records_locked(current_time)
            record = self._records.get(key)
            if record is None:
                execution_id = uuid.uuid4().hex
                self._records[key] = IdempotencyRecord(
                    status=IdempotencyStatus.RUNNING,
                    request_fingerprint=request_fingerprint,
                    execution_id=execution_id,
                    created_at=current_time,
                    updated_at=current_time,
                )
                owner = True
            else:
                if record.request_fingerprint != request_fingerprint:
                    raise ValueError("同一幂等键不能复用于不同请求内容。")
                if record.status is IdempotencyStatus.SUCCESS:
                    return cast(T, record.result)
                if record.status is IdempotencyStatus.UNKNOWN:
                    raise RuntimeError("该幂等请求结果未知，必须先完成外部副作用对账后才能重试。")

                execution_id = record.execution_id
                owner = False
                deadline = current_time + timeout
                while True:
                    current = self._records.get(key)
                    if current is None:
                        raise RuntimeError("幂等记录已被对账流程释放，请重新提交请求。")
                    if current.execution_id != execution_id:
                        raise RuntimeError("幂等请求执行代次已变化，请查询最终状态。")
                    if current.status is IdempotencyStatus.SUCCESS:
                        return cast(T, current.result)
                    if current.status is IdempotencyStatus.UNKNOWN:
                        raise RuntimeError("该幂等请求结果未知，必须先完成外部副作用对账后才能重试。")
                    remaining = deadline - self._now()
                    if remaining <= 0:
                        raise TimeoutError("等待相同幂等请求完成超时，请查询最终状态，禁止自动重试。")
                    self._condition.wait(remaining)

        if not owner:
            raise RuntimeError("不可达代码。")

        try:
            result = operation(execution_id)
        except BaseException as error:
            with self._condition:
                current = self._records.get(key)
                if current is not None and current.execution_id == execution_id and current.status is IdempotencyStatus.RUNNING:
                    current.status = IdempotencyStatus.UNKNOWN
                    current.updated_at = self._now()
                    current.error_type = type(error).__name__
                    self._condition.notify_all()
            raise

        with self._condition:
            current = self._records.get(key)
            if current is not None and current.execution_id == execution_id:
                # 没有新的执行代次时，原 owner 返回成功即可安全收敛为 SUCCESS。
                current.status = IdempotencyStatus.SUCCESS
                current.result = result
                current.updated_at = self._now()
                current.error_type = None
                self._condition.notify_all()
        return result

    def mark_stale_running_unknown(self, max_running_seconds: float) -> list[str]:
        """将长期运行的请求标记为 UNKNOWN，绝不自动释放重试。"""
        if not math.isfinite(float(max_running_seconds)) or max_running_seconds <= 0:
            raise ValueError("max_running_seconds 必须为有限正数。")
        with self._condition:
            current_time = self._now()
            stale_keys: list[str] = []
            for key, record in self._records.items():
                if record.status is IdempotencyStatus.RUNNING and current_time - record.updated_at >= max_running_seconds:
                    record.status = IdempotencyStatus.UNKNOWN
                    record.updated_at = current_time
                    record.error_type = "StaleRunning"
                    stale_keys.append(key)
            if stale_keys:
                self._condition.notify_all()
            return stale_keys

    def get(self, key: str) -> IdempotencyRecord | None:
        """返回记录快照，避免调用方修改内部状态。"""
        with self._condition:
            record = self._records.get(key)
            if record is None:
                return None
            return IdempotencyRecord(
                status=record.status,
                request_fingerprint=record.request_fingerprint,
                execution_id=record.execution_id,
                created_at=record.created_at,
                updated_at=record.updated_at,
                result=record.result,
                error_type=record.error_type,
            )


if __name__ == "__main__":
    store = IdempotencyStore()
    call_count = [0]

    def create_ticket(execution_id: str) -> str:
        call_count[0] += 1
        # 实际应将 execution_id 传给下游创建工单接口作为幂等键。
        return f"TICKET-1001 ({execution_id[:8]})"

    print(store.execute("request-001", create_ticket, request_fingerprint="create:TICKET-1001"))
    print(store.execute("request-001", create_ticket, request_fingerprint="create:TICKET-1001"))
    print("实际执行次数:", call_count[0])
