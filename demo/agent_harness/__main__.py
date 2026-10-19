"""Run an agent request from the command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import Agent
from .model import ModelError, OllamaClient
from .tools import WorkspaceTools


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a small local agent over a workspace"
    )
    parser.add_argument("request", help="Task for the agent")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument(
        "--model", default="qwen3:8b", help="Installed Ollama model name"
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--allow-write", action="store_true")
    parser.add_argument(
        "--trace", action="store_true", help="Print tool calls and results"
    )
    args = parser.parse_args(argv)

    try:
        tools = WorkspaceTools(args.workspace, allow_write=args.allow_write)
        agent = Agent(OllamaClient(args.model, args.base_url), tools, args.max_steps)
        result = agent.run(args.request, trace=args.trace)
    except (ValueError, ModelError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.trace:
        for event in result.trace:
            print(json.dumps(event, ensure_ascii=False), file=sys.stderr)
    print(result.answer)
    return 1 if result.stopped_by_limit else 0


if __name__ == "__main__":
    raise SystemExit(main())
