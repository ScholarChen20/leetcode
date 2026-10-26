"""带确认、幂等键、协作式截止时间和不可信数据隔离的 Agent 工具调用实现。

关键原则：
1. Python 线程超时不能可靠取消已运行的写操作，因此 Runtime 不伪造“已取消”。
2. 写工具必须使用 ``ToolExecutionContext.idempotency_key`` 调用支持幂等的下游服务。
3. 写工具超时或未知异常时，结果按 ``UNKNOWN`` 处理并停止任务，禁止自动重试。
4. 用户确认绑定任务、工具、精确参数哈希、动作 ID、过期时间与一次性 nonce。
5. nonce 消费由可共享的 ``ConfirmationNonceStore`` 负责；生产环境应实现为 Redis/数据库。
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import json
import math
import numbers
import threading
import time
from typing import Protocol
import uuid


ArgumentValidator = Callable[[Mapping[str, object]], None]
OutputProjector = Callable[[object], Mapping[str, object]]
Clock = Callable[[], float]


class ToolRisk(str, Enum):
    """工具风险等级。"""

    READ_ONLY = "READ_ONLY"
    WRITE = "WRITE"


class ToolExecutionUnknown(Exception):
    """工具请求可能已到达下游，但当前调用方无法确认最终结果。"""


class ToolDeadlineExceeded(ToolExecutionUnknown):
    """下游工具按 Context 截止时间终止时应抛出的异常。"""


class ConfirmationNonceStore(Protocol):
    """一次性确认 nonce 的共享存储接口。"""

    def consume_if_available(self, nonce: str, expires_at: float, now: float) -> bool:
        """在 nonce 未使用且未过期时原子消费，成功返回 True。"""


class InMemoryConfirmationNonceStore:
    """进程内 nonce 存储，仅用于教学和单进程测试。

    多实例或重启场景必须替换为 Redis/数据库等共享持久化实现。
    """

    def __init__(self) -> None:
        self._consumed: dict[str, float] = {}
        self._lock = threading.Lock()

    def consume_if_available(self, nonce: str, expires_at: float, now: float) -> bool:
        """原子消费未过期 nonce，并清理已过期消费记录。"""
        with self._lock:
            expired = [key for key, expiry in self._consumed.items() if expiry <= now]
            for key in expired:
                del self._consumed[key]
            if now >= expires_at or nonce in self._consumed:
                return False
            self._consumed[nonce] = expires_at
            return True


@dataclass(frozen=True)
class ToolExecutionContext:
    """传给工具处理器的执行上下文。"""

    task_id: str
    execution_id: str
    action_id: str | None
    idempotency_key: str | None
    deadline_monotonic: float
    clock: Clock

    def remaining_seconds(self) -> float:
        """返回距离调用截止时间的剩余秒数。"""
        return max(0.0, self.deadline_monotonic - self.clock())

    def ensure_before_deadline(self) -> None:
        """供工具在发起远程请求前检查协作式截止时间。"""
        if self.remaining_seconds() <= 0:
            raise ToolDeadlineExceeded("工具调用已超过截止时间。")


ToolHandler = Callable[[Mapping[str, object], ToolExecutionContext], object]


@dataclass
class ToolDefinition:
    """工具处理器、参数 Schema、输出白名单和执行约束。

    ``handler`` 必须将 ``context.remaining_seconds()`` 映射为下游连接、读取或
    服务端 deadline。WRITE 工具必须把 ``context.idempotency_key`` 传给下游服务。
    """

    handler: ToolHandler
    validator: ArgumentValidator
    output_projector: OutputProjector
    risk: ToolRisk = ToolRisk.READ_ONLY
    timeout_seconds: float = 5.0
    max_output_chars: int = 2_000
    max_concurrency: int = 4
    _semaphore: threading.BoundedSemaphore = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not callable(self.handler) or not callable(self.validator) or not callable(self.output_projector):
            raise ValueError("handler、validator 和 output_projector 都必须可调用。")
        if not isinstance(self.risk, ToolRisk):
            raise ValueError("risk 必须是 ToolRisk。")
        try:
            timeout = float(self.timeout_seconds)
        except (TypeError, ValueError) as error:
            raise ValueError("timeout_seconds 必须是数值。") from error
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout_seconds 必须为有限正数。")
        if (
            not isinstance(self.max_output_chars, numbers.Integral)
            or isinstance(self.max_output_chars, bool)
            or self.max_output_chars <= 0
            or not isinstance(self.max_concurrency, numbers.Integral)
            or isinstance(self.max_concurrency, bool)
            or self.max_concurrency <= 0
        ):
            raise ValueError("max_output_chars 和 max_concurrency 必须为正整数。")
        self.timeout_seconds = timeout
        self.max_output_chars = int(self.max_output_chars)
        self.max_concurrency = int(self.max_concurrency)
        self._semaphore = threading.BoundedSemaphore(self.max_concurrency)


@dataclass(frozen=True)
class ToolCall:
    """模型规划出的结构化工具调用。arguments 必须可严格 JSON 序列化。"""

    tool_name: str
    arguments: Mapping[str, object]
    reasoning: str = ""


@dataclass(frozen=True)
class WriteConfirmation:
    """由服务端在用户确认后签发的一次性精确写操作授权。"""

    task_id: str
    tool_name: str
    arguments_hash: str
    action_id: str
    nonce: str
    expires_at: float
    signature: str


class ConfirmationAuthority:
    """以 HMAC 签发和消费精确写操作授权。

    生产环境由服务端保管 ``secret``，并注入 Redis/数据库实现的共享 ``nonce_store``。
    模型、浏览器和单个 Agent Runtime 均不应持有消费 nonce 的权限。
    """

    def __init__(self, secret: bytes, nonce_store: ConfirmationNonceStore, clock: Clock = time.monotonic) -> None:
        if not isinstance(secret, bytes) or len(secret) < 16 or not callable(clock):
            raise ValueError("secret 必须至少 16 字节，clock 必须可调用。")
        if not hasattr(nonce_store, "consume_if_available"):
            raise ValueError("nonce_store 必须实现 consume_if_available。")
        self._secret = secret
        self._nonce_store = nonce_store
        self._clock = clock

    def _now(self) -> float:
        now = float(self._clock())
        if not math.isfinite(now):
            raise ValueError("clock 必须返回有限单调时间。")
        return now

    @staticmethod
    def _payload(
        task_id: str,
        tool_name: str,
        arguments_hash: str,
        action_id: str,
        nonce: str,
        expires_at: float,
    ) -> bytes:
        return json.dumps(
            {
                "task_id": task_id,
                "tool_name": tool_name,
                "arguments_hash": arguments_hash,
                "action_id": action_id,
                "nonce": nonce,
                "expires_at": expires_at,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

    def issue(self, task_id: str, tool_name: str, arguments: Mapping[str, object], ttl_seconds: float = 60.0) -> WriteConfirmation:
        """为用户已经审阅过的精确工具参数签发一次性授权。"""
        try:
            ttl = float(ttl_seconds)
        except (TypeError, ValueError) as error:
            raise ValueError("ttl_seconds 必须是数值。") from error
        if not isinstance(task_id, str) or not task_id or not isinstance(tool_name, str) or not tool_name or not math.isfinite(ttl) or ttl <= 0:
            raise ValueError("task_id/tool_name 必须非空，ttl_seconds 必须为有限正数。")
        arguments_hash = _arguments_hash(arguments)
        expires_at = self._now() + ttl
        action_id = uuid.uuid4().hex
        nonce = uuid.uuid4().hex
        signature = hmac.new(
            self._secret,
            self._payload(task_id, tool_name, arguments_hash, action_id, nonce, expires_at),
            hashlib.sha256,
        ).hexdigest()
        return WriteConfirmation(task_id, tool_name, arguments_hash, action_id, nonce, expires_at, signature)

    def _verify_signature(self, grant: WriteConfirmation, task_id: str, tool_name: str, arguments_hash: str, now: float) -> bool:
        """校验授权的绑定信息、时效和 HMAC 签名。"""
        if grant.task_id != task_id or grant.tool_name != tool_name or grant.arguments_hash != arguments_hash:
            return False
        if now >= grant.expires_at:
            return False
        expected_signature = hmac.new(
            self._secret,
            self._payload(
                grant.task_id,
                grant.tool_name,
                grant.arguments_hash,
                grant.action_id,
                grant.nonce,
                grant.expires_at,
            ),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected_signature, grant.signature)

    def consume_if_valid(
        self,
        grant: WriteConfirmation,
        task_id: str,
        tool_name: str,
        arguments_hash: str,
    ) -> bool:
        """验证并在共享存储中原子消费授权 nonce。"""
        now = self._now()
        if not self._verify_signature(grant, task_id, tool_name, arguments_hash, now):
            return False
        return self._nonce_store.consume_if_available(grant.nonce, grant.expires_at, now)


class ObservationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ToolObservation:
    """低信任工具数据。

    ``data_json`` 只包含 output projector 白名单字段的 JSON 数据；Runtime 的写能力
    不依赖 Planner 是否遵守其中的自然语言内容。
    """

    status: ObservationStatus
    source: str
    data_json: str
    truncated: bool

    def as_model_data(self) -> dict[str, object]:
        """返回模型适配层可作为低信任 tool-result 消息注入的结构化数据。"""
        return {
            "status": self.status.value,
            "source": self.source,
            "data": json.loads(self.data_json),
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class ExecutionStep:
    """Agent 的单步执行审计记录；不保存原始敏感参数。"""

    reasoning: str
    tool_name: str
    arguments_hash: str
    observation: ToolObservation


def _canonical_arguments(arguments: Mapping[str, object]) -> str:
    """将工具参数编码成稳定且不含 NaN/Inf 的 JSON。"""
    if not isinstance(arguments, Mapping):
        raise ValueError("arguments 必须是 Mapping。")
    try:
        return json.dumps(dict(arguments), sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("arguments 必须可 JSON 序列化且不含 NaN/Inf。") from error


def _arguments_hash(arguments: Mapping[str, object]) -> str:
    """返回精确工具参数的 SHA-256 摘要。"""
    return hashlib.sha256(_canonical_arguments(arguments).encode("utf-8")).hexdigest()


def _json_data(value: Mapping[str, object]) -> str:
    """仅允许 projector 返回可 JSON 序列化的结构化数据。"""
    if not isinstance(value, Mapping):
        raise ValueError("output_projector 必须返回 Mapping。")
    try:
        return json.dumps(dict(value), sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("output_projector 返回的数据必须可 JSON 序列化且不含 NaN/Inf。") from error


def _project_untrusted_output(value: object, projector: OutputProjector, max_output_chars: int) -> ToolObservation:
    """只保留经过白名单投影的有限长度 JSON 工具数据。"""
    serialized = _json_data(projector(value))
    if len(serialized) <= max_output_chars:
        return ToolObservation(
            status=ObservationStatus.SUCCESS,
            source="UNTRUSTED_TOOL_DATA",
            data_json=serialized,
            truncated=False,
        )
    preview = serialized[:max_output_chars]
    return ToolObservation(
        status=ObservationStatus.SUCCESS,
        source="UNTRUSTED_TOOL_DATA",
        data_json=json.dumps({"truncated": True, "preview": preview}, ensure_ascii=False, separators=(",", ":")),
        truncated=True,
    )


class ToolCallingAgent:
    """带工具契约、共享写授权和结果未知保护的最小 Agent Runtime。"""

    def __init__(
        self,
        tools: Mapping[str, ToolDefinition],
        confirmation_authority: ConfirmationAuthority,
        max_steps: int = 8,
        max_same_call: int = 2,
        clock: Clock = time.monotonic,
    ) -> None:
        if (
            not tools
            or not callable(clock)
            or not isinstance(max_steps, numbers.Integral)
            or isinstance(max_steps, bool)
            or not isinstance(max_same_call, numbers.Integral)
            or isinstance(max_same_call, bool)
            or max_steps <= 0
            or max_same_call <= 0
        ):
            raise ValueError("tools 不能为空，clock 必须可调用，步骤限制必须为正整数。")
        self._tools = dict(tools)
        self._confirmation_authority = confirmation_authority
        self._max_steps = int(max_steps)
        self._max_same_call = int(max_same_call)
        self._clock = clock

    def _now(self) -> float:
        now = float(self._clock())
        if not math.isfinite(now):
            raise ValueError("clock 必须返回有限单调时间。")
        return now

    @staticmethod
    def _failure_observation(status: ObservationStatus, code: str) -> ToolObservation:
        """创建不泄露外部原始异常和敏感数据的失败 Observation。"""
        return ToolObservation(status=status, source="RUNTIME", data_json=json.dumps({"code": code}), truncated=False)

    def _consume_matching_confirmation(
        self,
        task_id: str,
        tool_name: str,
        arguments_hash: str,
        confirmations: Collection[WriteConfirmation],
    ) -> WriteConfirmation | None:
        """在共享 nonce 存储中消费与当前精确动作匹配的一次性授权。"""
        for grant in confirmations:
            if self._confirmation_authority.consume_if_valid(grant, task_id, tool_name, arguments_hash):
                return grant
        return None

    def _execute_tool(
        self,
        definition: ToolDefinition,
        task_id: str,
        arguments: Mapping[str, object],
        action_id: str | None,
    ) -> ToolObservation:
        """同步调用协作式工具。

        Runtime 不强行终止线程；若 WRITE 工具在 deadline 后返回，结果仍按 UNKNOWN
        处理，避免把可能晚到的副作用误报为成功。
        """
        if not definition._semaphore.acquire(blocking=False):
            return self._failure_observation(ObservationStatus.FAILED, "TOOL_BUSY")
        try:
            now = self._now()
            context = ToolExecutionContext(
                task_id=task_id,
                execution_id=uuid.uuid4().hex,
                action_id=action_id,
                idempotency_key=action_id if definition.risk is ToolRisk.WRITE else None,
                deadline_monotonic=now + definition.timeout_seconds,
                clock=self._clock,
            )
            context.ensure_before_deadline()
            result = definition.handler(dict(arguments), context)
            if context.remaining_seconds() <= 0:
                if definition.risk is ToolRisk.WRITE:
                    return self._failure_observation(ObservationStatus.UNKNOWN, "WRITE_DEADLINE_EXCEEDED")
                return self._failure_observation(ObservationStatus.FAILED, "READ_DEADLINE_EXCEEDED")
            return _project_untrusted_output(result, definition.output_projector, definition.max_output_chars)
        except ToolExecutionUnknown:
            status = ObservationStatus.UNKNOWN if definition.risk is ToolRisk.WRITE else ObservationStatus.FAILED
            return self._failure_observation(status, "TOOL_RESULT_UNKNOWN")
        except ValueError:
            return self._failure_observation(ObservationStatus.FAILED, "INVALID_TOOL_INPUT_OR_OUTPUT")
        except Exception:
            if definition.risk is ToolRisk.WRITE:
                return self._failure_observation(ObservationStatus.UNKNOWN, "WRITE_TOOL_UNCONFIRMED_FAILURE")
            return self._failure_observation(ObservationStatus.FAILED, "READ_TOOL_FAILURE")
        finally:
            definition._semaphore.release()

    def run(
        self,
        task_id: str,
        task: str,
        planner: Callable[[str, list[ExecutionStep]], ToolCall | str],
        confirmations: Collection[WriteConfirmation] = (),
    ) -> tuple[str, list[ExecutionStep]]:
        """执行 Agent 任务。

        模型适配层应将 ``observation.as_model_data()`` 作为低信任 tool-result 数据传入。
        无论模型如何解读不可信内容，WRITE 工具均必须通过 Runtime 的精确确认门禁。
        """
        if not isinstance(task_id, str) or not task_id or not isinstance(task, str) or not task:
            raise ValueError("task_id 和 task 必须是非空字符串。")
        steps: list[ExecutionStep] = []
        repeated_calls: dict[str, int] = {}
        for _ in range(self._max_steps):
            decision = planner(task, steps)
            if isinstance(decision, str):
                return decision, steps
            if not isinstance(decision, ToolCall):
                return "执行已停止：planner 输出不是合法的 ToolCall 或最终答案。", steps

            definition = self._tools.get(decision.tool_name)
            if definition is None:
                steps.append(
                    ExecutionStep(
                        decision.reasoning,
                        decision.tool_name,
                        "",
                        self._failure_observation(ObservationStatus.FAILED, "TOOL_NOT_FOUND"),
                    )
                )
                continue

            try:
                arguments_hash = _arguments_hash(decision.arguments)
                definition.validator(decision.arguments)
            except ValueError:
                steps.append(
                    ExecutionStep(
                        decision.reasoning,
                        decision.tool_name,
                        "",
                        self._failure_observation(ObservationStatus.FAILED, "INVALID_TOOL_ARGUMENTS"),
                    )
                )
                continue

            call_signature = f"{decision.tool_name}:{arguments_hash}"
            repeated_calls[call_signature] = repeated_calls.get(call_signature, 0) + 1
            if repeated_calls[call_signature] > self._max_same_call:
                return "执行已停止：检测到重复工具调用。", steps

            action_id: str | None = None
            if definition.risk is ToolRisk.WRITE:
                grant = self._consume_matching_confirmation(task_id, decision.tool_name, arguments_hash, confirmations)
                if grant is None:
                    steps.append(
                        ExecutionStep(
                            decision.reasoning,
                            decision.tool_name,
                            arguments_hash,
                            self._failure_observation(ObservationStatus.FAILED, "WRITE_CONFIRMATION_REQUIRED"),
                        )
                    )
                    continue
                action_id = grant.action_id

            observation = self._execute_tool(definition, task_id, decision.arguments, action_id)
            steps.append(ExecutionStep(decision.reasoning, decision.tool_name, arguments_hash, observation))
            if definition.risk is ToolRisk.WRITE and observation.status is ObservationStatus.UNKNOWN:
                return "执行已停止：写操作结果未知，请先对账或人工处理，禁止自动重试。", steps
        return "执行已停止：达到最大步骤数。", steps


if __name__ == "__main__":
    def lookup_order(arguments: Mapping[str, object], context: ToolExecutionContext) -> dict[str, str]:
        context.ensure_before_deadline()
        return {"status": {"A100": "已支付"}.get(str(arguments["order_id"]), "未找到")}

    def validate_order_id(arguments: Mapping[str, object]) -> None:
        if set(arguments) != {"order_id"} or not isinstance(arguments.get("order_id"), str):
            raise ValueError("只允许传入字符串 order_id。")

    def project_order(value: object) -> Mapping[str, object]:
        if not isinstance(value, dict) or not isinstance(value.get("status"), str):
            raise ValueError("订单工具返回格式异常。")
        return {"status": value["status"]}

    def planner(_: str, steps: list[ExecutionStep]) -> ToolCall | str:
        if not steps:
            return ToolCall("lookup_order", {"order_id": "A100"}, "先查询订单状态。")
        return steps[-1].observation.data_json

    nonce_store = InMemoryConfirmationNonceStore()
    authority = ConfirmationAuthority(b"demo-confirmation-secret-32-bytes", nonce_store)
    agent = ToolCallingAgent(
        {
            "lookup_order": ToolDefinition(
                lookup_order,
                validate_order_id,
                project_order,
                risk=ToolRisk.READ_ONLY,
            )
        },
        authority,
    )
    answer, trace = agent.run("task-order-001", "查询订单 A100", planner)
    print(answer)
    print(trace)
