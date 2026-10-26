"""支持认领、租约、已知失败重试和未知结果隔离的内存任务队列。

安全语义：
- 下游写操作必须使用稳定 ``task_id`` 作为幂等键，而不是每次变化的 ``lease_id``。
- ``lease_generation`` 是单调递增的 fencing generation；下游若需要防止旧工作者提交，
  必须原子保存并拒绝较旧 generation。
- 租约过期时任务进入 ``UNKNOWN``，不会自动重新执行。只有对账确认无副作用后才可恢复。
"""

from __future__ import annotations

from collections.abc import Callable
import copy
from dataclasses import dataclass
from enum import Enum
import math
import numbers
import threading
import time
import uuid


Clock = Callable[[], float]


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Task:
    """提供给调用方的不可变任务快照。"""

    task_id: str
    payload: object
    max_retries: int
    status: TaskStatus
    attempts: int
    next_run_at: float
    last_error: str | None
    created_at: float
    lease_id: str | None
    lease_generation: int
    lease_expires_at: float | None
    idempotency_key: str


@dataclass
class _TaskRecord:
    """仅队列内部可变的任务状态。"""

    task_id: str
    payload: object
    max_retries: int
    created_at: float
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    next_run_at: float = 0.0
    last_error: str | None = None
    lease_id: str | None = None
    lease_generation: int = 0
    lease_expires_at: float | None = None


class InMemoryTaskQueue:
    """用于理解安全任务状态机的线程安全队列，不用于生产持久化场景。"""

    def __init__(self, clock: Clock = time.monotonic) -> None:
        if not callable(clock):
            raise ValueError("clock 必须可调用。")
        self._clock = clock
        self._tasks: dict[str, _TaskRecord] = {}
        self._lock = threading.Lock()

    def _now(self) -> float:
        current_time = float(self._clock())
        if not math.isfinite(current_time):
            raise ValueError("clock 必须返回有限单调时间。")
        return current_time

    @staticmethod
    def _snapshot(task: _TaskRecord) -> Task:
        return Task(
            task_id=task.task_id,
            payload=copy.deepcopy(task.payload),
            max_retries=task.max_retries,
            status=task.status,
            attempts=task.attempts,
            next_run_at=task.next_run_at,
            last_error=task.last_error,
            created_at=task.created_at,
            lease_id=task.lease_id,
            lease_generation=task.lease_generation,
            lease_expires_at=task.lease_expires_at,
            idempotency_key=task.task_id,
        )

    def _mark_expired_unknown_locked(self, current_time: float) -> int:
        """将过期租约标为结果未知，绝不自动重新调度。"""
        marked_unknown = 0
        for task in self._tasks.values():
            if task.status is TaskStatus.RUNNING and task.lease_expires_at is not None and task.lease_expires_at <= current_time:
                task.status = TaskStatus.UNKNOWN
                task.last_error = "工作者租约过期，外部副作用结果未知。"
                task.lease_id = None
                task.lease_expires_at = None
                marked_unknown += 1
        return marked_unknown

    def enqueue(self, payload: object, max_retries: int = 3) -> str:
        """创建并返回待执行任务 ID；该 ID 也是下游稳定幂等键。"""
        if not isinstance(max_retries, numbers.Integral) or isinstance(max_retries, bool) or max_retries < 0:
            raise ValueError("max_retries 必须是非负整数。")
        with self._lock:
            current_time = self._now()
            task = _TaskRecord(
                task_id=uuid.uuid4().hex,
                payload=copy.deepcopy(payload),
                max_retries=int(max_retries),
                created_at=current_time,
                next_run_at=current_time,
            )
            self._tasks[task.task_id] = task
            return task.task_id

    def claim(self, lease_seconds: float = 30.0) -> Task | None:
        """认领一个待执行任务，返回稳定幂等键和递增 fencing generation。"""
        try:
            lease_duration = float(lease_seconds)
        except (TypeError, ValueError) as error:
            raise ValueError("lease_seconds 必须是数值。") from error
        if not math.isfinite(lease_duration) or lease_duration <= 0:
            raise ValueError("lease_seconds 必须为有限正数。")
        with self._lock:
            current_time = self._now()
            self._mark_expired_unknown_locked(current_time)
            candidates = [task for task in self._tasks.values() if task.status is TaskStatus.PENDING and task.next_run_at <= current_time]
            if not candidates:
                return None
            task = min(candidates, key=lambda item: item.created_at)
            task.status = TaskStatus.RUNNING
            task.attempts += 1
            task.lease_generation += 1
            task.lease_id = uuid.uuid4().hex
            task.lease_expires_at = current_time + lease_duration
            return self._snapshot(task)

    def acknowledge(self, task_id: str, lease_id: str, lease_generation: int) -> None:
        """仅当前租约和 generation 对应的工作者可确认任务成功。"""
        with self._lock:
            current_time = self._now()
            self._mark_expired_unknown_locked(current_time)
            task = self._tasks[task_id]
            if (
                task.status is not TaskStatus.RUNNING
                or task.lease_id != lease_id
                or task.lease_generation != lease_generation
            ):
                raise RuntimeError("只能由持有当前租约和 generation 的工作者确认任务。")
            task.status = TaskStatus.SUCCESS
            task.lease_id = None
            task.lease_expires_at = None

    def fail(
        self,
        task_id: str,
        lease_id: str,
        lease_generation: int,
        error: str,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        """处理已知失败；只有明确确认未产生未知副作用时才进入自动重试。"""
        try:
            retry_delay = float(retry_delay_seconds)
        except (TypeError, ValueError) as error_value:
            raise ValueError("retry_delay_seconds 必须是数值。") from error_value
        if not math.isfinite(retry_delay) or retry_delay < 0:
            raise ValueError("retry_delay_seconds 必须是非负有限数。")
        with self._lock:
            current_time = self._now()
            self._mark_expired_unknown_locked(current_time)
            task = self._tasks[task_id]
            if (
                task.status is not TaskStatus.RUNNING
                or task.lease_id != lease_id
                or task.lease_generation != lease_generation
            ):
                raise RuntimeError("只能由持有当前租约和 generation 的工作者标记任务失败。")
            task.last_error = str(error)[:1_000]
            task.lease_id = None
            task.lease_expires_at = None
            if task.attempts <= task.max_retries:
                task.status = TaskStatus.PENDING
                task.next_run_at = current_time + retry_delay
            else:
                task.status = TaskStatus.FAILED

    def mark_expired_unknown(self) -> int:
        """主动将租约过期任务标为 UNKNOWN，返回数量。"""
        with self._lock:
            return self._mark_expired_unknown_locked(self._now())

    def resume_unknown_after_reconciliation(self, task_id: str, confirmed_not_executed: bool) -> None:
        """对账确认没有产生副作用后，人工恢复 UNKNOWN 任务。

        后续执行继续使用同一 ``task_id`` 作为下游幂等键；下游还应利用递增
        ``lease_generation`` 拒绝旧工作者迟到的提交。
        """
        if not confirmed_not_executed:
            raise ValueError("只有确认下游未产生副作用后才能恢复 UNKNOWN 任务。")
        with self._lock:
            task = self._tasks[task_id]
            if task.status is not TaskStatus.UNKNOWN:
                raise RuntimeError("只能恢复 UNKNOWN 状态的任务。")
            task.status = TaskStatus.PENDING
            task.next_run_at = self._now()
            task.last_error = "已完成对账，允许重新执行。"

    def get(self, task_id: str) -> Task:
        """读取任务当前状态快照，外部无法修改队列内部状态。"""
        with self._lock:
            return self._snapshot(self._tasks[task_id])


if __name__ == "__main__":
    fake_now = [0.0]
    queue = InMemoryTaskQueue(clock=lambda: fake_now[0])
    identifier = queue.enqueue({"task": "生成日报"}, max_retries=1)
    task = queue.claim()
    assert task is not None and task.lease_id is not None
    queue.fail(task.task_id, task.lease_id, task.lease_generation, "外部服务明确失败", retry_delay_seconds=0)
    retried = queue.claim()
    assert retried is not None and retried.lease_id is not None
    queue.acknowledge(retried.task_id, retried.lease_id, retried.lease_generation)
    print(queue.get(identifier))
