"""教学版只读 ReAct Agent：Thought -> Action -> Observation。

此示例仅允许只读工具。涉及创建、删除、发送等写操作时，应使用
``06_Agent工程化/01_tool_call_agent_loop.py`` 中带确认、幂等键和结果未知保护的实现。
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import inspect
import json
import numbers


ReadOnlyTool = Callable[..., object]
ArgumentValidator = Callable[[Mapping[str, object]], None]
OutputProjector = Callable[[object], str]
Planner = Callable[[str, list["AgentStep"]], "ToolCall | str"]


@dataclass(frozen=True)
class ReadOnlyToolSpec:
    """只读工具的参数校验和安全输出投影规则。"""

    handler: ReadOnlyTool
    validator: ArgumentValidator
    output_projector: OutputProjector
    max_output_chars: int = 2_000

    def __post_init__(self) -> None:
        if not callable(self.handler) or not callable(self.validator) or not callable(self.output_projector):
            raise ValueError("handler、validator 和 output_projector 都必须可调用。")
        if (
            not isinstance(self.max_output_chars, numbers.Integral)
            or isinstance(self.max_output_chars, bool)
            or self.max_output_chars <= 0
        ):
            raise ValueError("max_output_chars 必须为正整数。")


@dataclass(frozen=True)
class ToolCall:
    """模型规划出的只读工具调用。arguments 必须能被 JSON 严格序列化。"""

    name: str
    arguments: Mapping[str, object]
    thought: str = ""


@dataclass(frozen=True)
class ToolObservation:
    """工具返回的低信任数据，不应被当作系统指令执行。"""

    status: str
    source: str
    content: str
    truncated: bool


@dataclass(frozen=True)
class AgentStep:
    """单轮 Agent 执行记录。"""

    thought: str
    action: str
    arguments_hash: str
    observation: ToolObservation


def _canonical_arguments(arguments: Mapping[str, object]) -> str:
    """将工具参数编码为稳定 JSON，用于重复调用检测。"""
    try:
        return json.dumps(dict(arguments), sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("工具参数必须是可 JSON 序列化且不含 NaN/Inf 的数据。") from error


def _project_untrusted_output(value: object, projector: OutputProjector, max_output_chars: int) -> ToolObservation:
    """只将工具定义明确投影出的字段带入 Agent 历史，并限制长度。"""
    content = projector(value)
    if not isinstance(content, str):
        raise ValueError("output_projector 必须返回字符串。")
    compact_content = content[:max_output_chars]
    return ToolObservation(
        status="SUCCESS",
        source="UNTRUSTED_TOOL_DATA",
        content=compact_content,
        truncated=len(content) > max_output_chars,
    )


class ReActAgent:
    """通过外部 planner 模拟 LLM 决策的只读 ReAct 执行器。"""

    def __init__(self, tools: Mapping[str, ReadOnlyToolSpec], max_steps: int = 8, max_repeated_calls: int = 2) -> None:
        if (
            not isinstance(max_steps, numbers.Integral)
            or isinstance(max_steps, bool)
            or not isinstance(max_repeated_calls, numbers.Integral)
            or isinstance(max_repeated_calls, bool)
            or max_steps <= 0
            or max_repeated_calls <= 0
        ):
            raise ValueError("max_steps 和 max_repeated_calls 必须为正整数。")
        if not tools:
            raise ValueError("至少需要注册一个只读工具。")
        self.tools = dict(tools)
        self.max_steps = int(max_steps)
        self.max_repeated_calls = int(max_repeated_calls)

    @staticmethod
    def _validate_arguments(tool: ReadOnlyToolSpec, arguments: Mapping[str, object]) -> None:
        """校验必填参数、未知参数和业务 Schema。"""
        try:
            inspect.signature(tool.handler).bind(**dict(arguments))
        except TypeError as error:
            raise ValueError(f"工具参数不合法：{error}") from error
        tool.validator(arguments)

    def run(self, task: str, planner: Planner) -> tuple[str, list[AgentStep]]:
        """执行只读任务；工具输出始终以低信任 Observation 反馈给 planner。"""
        if not isinstance(task, str) or not task:
            raise ValueError("task 必须是非空字符串。")
        history: list[AgentStep] = []
        call_counts: dict[str, int] = {}
        for _ in range(self.max_steps):
            decision = planner(task, history)
            if isinstance(decision, str):
                return decision, history
            if not isinstance(decision, ToolCall) or not isinstance(decision.arguments, Mapping):
                return "任务终止：planner 输出不是合法的 ToolCall 或最终答案。", history

            tool = self.tools.get(decision.name)
            if tool is None:
                history.append(
                    AgentStep(
                        decision.thought,
                        decision.name,
                        "",
                        ToolObservation("FAILED", "RUNTIME", "工具不存在。", False),
                    )
                )
                continue

            try:
                canonical_arguments = _canonical_arguments(decision.arguments)
                call_key = f"{decision.name}:{canonical_arguments}"
                call_counts[call_key] = call_counts.get(call_key, 0) + 1
                if call_counts[call_key] > self.max_repeated_calls:
                    return "任务终止：检测到重复只读工具调用。", history
                self._validate_arguments(tool, decision.arguments)
                observation = _project_untrusted_output(
                    tool.handler(**dict(decision.arguments)),
                    tool.output_projector,
                    tool.max_output_chars,
                )
            except ValueError as error:
                observation = ToolObservation("FAILED", "RUNTIME", f"工具参数或输出不合法：{error}", False)
                canonical_arguments = ""
            except Exception as error:
                observation = ToolObservation("FAILED", "RUNTIME", f"工具执行失败：{type(error).__name__}", False)
                canonical_arguments = ""
            history.append(AgentStep(decision.thought, decision.name, canonical_arguments, observation))
        return "任务终止：达到最大执行步数。", history


if __name__ == "__main__":
    def calculator(expression: str) -> dict[str, int]:
        if expression == "2+3":
            return {"result": 5}
        raise ValueError("仅演示 2+3。")

    def validate_expression(arguments: Mapping[str, object]) -> None:
        if arguments.get("expression") != "2+3":
            raise ValueError("expression 仅允许 2+3。")

    def project_result(value: object) -> str:
        if not isinstance(value, dict) or not isinstance(value.get("result"), int):
            raise ValueError("计算工具返回格式异常。")
        return f"计算结果：{value['result']}"

    def demo_planner(_: str, history: list[AgentStep]) -> ToolCall | str:
        if not history:
            return ToolCall("calculator", {"expression": "2+3"}, "需要先计算表达式。")
        return history[-1].observation.content

    agent = ReActAgent(
        {"calculator": ReadOnlyToolSpec(calculator, validate_expression, project_result)}
    )
    answer, steps = agent.run("计算 2+3", demo_planner)
    print("最终答案:", answer)
    print("执行记录:", steps)
