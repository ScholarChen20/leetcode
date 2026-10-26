"""按依赖关系执行多 Agent / 多任务 DAG 的调度实现。"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass


TaskFunction = Callable[[Mapping[str, object]], object]


@dataclass(frozen=True)
class ScheduledTask:
    """带依赖声明的任务。"""

    task_id: str
    dependencies: tuple[str, ...]
    run: TaskFunction


class DagTaskScheduler:
    """拓扑排序并顺序执行 DAG；无依赖任务可在生产中改造成并行。"""

    def __init__(self, tasks: Sequence[ScheduledTask]) -> None:
        task_list = list(tasks)
        self._tasks = {task.task_id: task for task in task_list}
        if len(self._tasks) != len(task_list):
            raise ValueError("task_id 不能重复。")
        for task in task_list:
            missing = set(task.dependencies) - self._tasks.keys()
            if missing:
                raise ValueError(f"任务 {task.task_id} 依赖不存在：{missing}")

    def execute(self) -> dict[str, object]:
        """按拓扑顺序执行所有任务并返回结果字典。"""
        pending = set(self._tasks)
        results: dict[str, object] = {}
        while pending:
            ready = [task_id for task_id in pending if all(dependency in results for dependency in self._tasks[task_id].dependencies)]
            if not ready:
                raise ValueError("任务依赖存在环，无法调度。")
            for task_id in sorted(ready):
                task = self._tasks[task_id]
                dependency_results = {dependency: results[dependency] for dependency in task.dependencies}
                results[task_id] = task.run(dependency_results)
                pending.remove(task_id)
        return results


if __name__ == "__main__":
    scheduler = DagTaskScheduler(
        [
            ScheduledTask("search", (), lambda _: "搜索结果"),
            ScheduledTask("analyze", ("search",), lambda data: f"分析：{data['search']}"),
            ScheduledTask("report", ("analyze",), lambda data: f"报告：{data['analyze']}"),
        ]
    )
    print(scheduler.execute())
