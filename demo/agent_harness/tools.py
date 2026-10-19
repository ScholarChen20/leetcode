"""Workspace-scoped tools and their model-facing schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ToolError(ValueError):
    """A tool request is invalid or denied."""


class WorkspaceTools:
    def __init__(
        self,
        workspace: Path,
        allow_write: bool = False,
        max_read_chars: int = 12_000,
        max_entries: int = 100,
    ) -> None:
        self.workspace = workspace.resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace is not a directory: {workspace}")
        self.allow_write = allow_write
        self.max_read_chars = max_read_chars
        self.max_entries = max_entries

    def schemas(self) -> list[dict]:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files and directories under the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative directory path; default ."},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a UTF-8 text file under the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string", "description": "Relative file path"}},
                        "required": ["path"],
                    },
                },
            },
        ]
        if self.allow_write:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "write_file",
                        "description": "Write a UTF-8 file under the workspace. Existing files require overwrite=true.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Relative file path"},
                                "content": {"type": "string"},
                                "overwrite": {"type": "boolean", "description": "Replace an existing file; default false"},
                            },
                            "required": ["path", "content"],
                        },
                    },
                }
            )
        return tools

    def _resolve(self, relative: str) -> Path:
        if not isinstance(relative, str) or not relative.strip():
            raise ToolError("path must be a non-empty string")
        candidate = Path(relative)
        if candidate.is_absolute():
            raise ToolError("absolute paths are not allowed")
        target = (self.workspace / candidate).resolve()
        if not target.is_relative_to(self.workspace):
            raise ToolError("path escapes the workspace")
        if ".git" in candidate.parts or ".git" in target.relative_to(self.workspace).parts:
            raise ToolError("Git metadata is not accessible")
        return target

    def list_files(self, path: str = ".") -> dict:
        directory = self._resolve(path)
        if not directory.is_dir():
            raise ToolError("path is not a directory")
        entries = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        visible = [entry for entry in entries if entry.name != ".git"]
        result = []
        for entry in visible[: self.max_entries]:
            # Resolved symlinks outside the workspace are omitted.
            if not entry.resolve().is_relative_to(self.workspace):
                continue
            result.append(
                {
                    "path": entry.relative_to(self.workspace).as_posix(),
                    "type": "directory" if entry.is_dir() else "file",
                }
            )
        return {"entries": result, "truncated": len(visible) > self.max_entries}

    def read_file(self, path: str) -> dict:
        target = self._resolve(path)
        if not target.is_file():
            raise ToolError("path is not a file")
        try:
            with target.open("r", encoding="utf-8") as stream:
                content = stream.read(self.max_read_chars + 1)
        except (UnicodeError, OSError) as exc:
            raise ToolError(f"cannot read UTF-8 file: {exc}") from exc
        return {
            "path": target.relative_to(self.workspace).as_posix(),
            "content": content[: self.max_read_chars],
            "truncated": len(content) > self.max_read_chars,
        }

    def write_file(self, path: str, content: str, overwrite: bool = False) -> dict:
        if not self.allow_write:
            raise ToolError("write access is disabled; restart with --allow-write")
        target = self._resolve(path)
        if target == self.workspace:
            raise ToolError("path must name a file")
        if not isinstance(content, str):
            raise ToolError("content must be a string")
        if len(content) > 20_000:
            raise ToolError("content exceeds the 20,000-character write limit")
        if not isinstance(overwrite, bool):
            raise ToolError("overwrite must be a boolean")
        if not target.parent.is_dir():
            raise ToolError("parent directory does not exist")
        try:
            with target.open("w" if overwrite else "x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        except FileExistsError as exc:
            raise ToolError("file exists; set overwrite=true to replace it") from exc
        except OSError as exc:
            raise ToolError(f"cannot write file: {exc}") from exc
        return {"path": target.relative_to(self.workspace).as_posix(), "characters": len(content)}

    def execute(self, name: str, arguments: Any) -> str:
        try:
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            if not isinstance(arguments, dict):
                raise ToolError("arguments must be a JSON object")
            allowed = {"list_files": self.list_files, "read_file": self.read_file}
            if self.allow_write:
                allowed["write_file"] = self.write_file
            operation = allowed.get(name)
            if operation is None:
                raise ToolError(f"unknown or disabled tool: {name}")
            result = operation(**arguments)
            return json.dumps({"ok": True, "result": result}, ensure_ascii=False)
        except (ToolError, TypeError, ValueError) as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)
