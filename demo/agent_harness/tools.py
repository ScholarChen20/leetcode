"""File tools limited to one workspace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


MAX_WRITE_CHARS = 20_000
DEFAULT_READ_CHARS = 12_000
DEFAULT_LIST_ENTRIES = 100

ToolResult = dict[str, Any]


class ToolError(ValueError):
    """A tool call is invalid or is outside the allowed workspace."""


def _tool_schema(
    name: str,
    description: str,
    properties: dict[str, dict[str, str]],
    required: list[str] | None = None,
) -> dict[str, Any]:
    parameters: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        parameters["required"] = required
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


PATH_PROPERTY = {"type": "string", "description": "Path relative to the workspace"}
TOOL_SCHEMAS = (
    _tool_schema(
        "list_files",
        "List files and directories under the workspace.",
        {
            "path": {
                "type": "string",
                "description": "Relative directory; defaults to .",
            }
        },
    ),
    _tool_schema(
        "read_file",
        "Read a UTF-8 text file under the workspace.",
        {"path": PATH_PROPERTY},
        ["path"],
    ),
    _tool_schema(
        "write_file",
        "Write a UTF-8 file. Existing files require overwrite=true.",
        {
            "path": PATH_PROPERTY,
            "content": {"type": "string", "description": "Text to write"},
            "overwrite": {"type": "boolean", "description": "Replace an existing file"},
        },
        ["path", "content"],
    ),
)


class WorkspaceTools:
    def __init__(
        self,
        workspace: Path,
        allow_write: bool = False,
        max_read_chars: int = DEFAULT_READ_CHARS,
        max_entries: int = DEFAULT_LIST_ENTRIES,
    ) -> None:
        self.workspace = workspace.resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace is not a directory: {workspace}")
        if max_read_chars < 1 or max_entries < 1:
            raise ValueError("tool limits must be positive")
        self.allow_write = allow_write
        self.max_read_chars = max_read_chars
        self.max_entries = max_entries

    def schemas(self) -> list[dict[str, Any]]:
        """Return only the tools enabled for this run."""
        count = len(TOOL_SCHEMAS) if self.allow_write else len(TOOL_SCHEMAS) - 1
        return list(TOOL_SCHEMAS[:count])

    def _is_visible_entry(self, entry: Path) -> bool:
        if entry.name == ".git":
            return False
        target = entry.resolve()
        if not target.is_relative_to(self.workspace):
            return False
        return ".git" not in target.relative_to(self.workspace).parts

    def _display_path(self, target: Path) -> str:
        return target.relative_to(self.workspace).as_posix()

    def _resolve(self, relative: str) -> Path:
        if not isinstance(relative, str) or not relative.strip():
            raise ToolError("path must be a non-empty string")
        candidate = Path(relative)
        if candidate.is_absolute():
            raise ToolError("absolute paths are not allowed")
        target = (self.workspace / candidate).resolve()
        if not target.is_relative_to(self.workspace):
            raise ToolError("path escapes the workspace")
        relative_parts = target.relative_to(self.workspace).parts
        if ".git" in candidate.parts or ".git" in relative_parts:
            raise ToolError("Git metadata is not accessible")
        return target

    def list_files(self, path: str = ".") -> ToolResult:
        directory = self._resolve(path)
        if not directory.is_dir():
            raise ToolError("path is not a directory")
        try:
            entries = sorted(
                directory.iterdir(), key=lambda entry: entry.name.casefold()
            )
            visible = [entry for entry in entries if self._is_visible_entry(entry)]
        except OSError as exc:
            raise ToolError(f"cannot list directory: {exc}") from exc

        return {
            "entries": [
                {
                    "path": self._display_path(entry),
                    "type": "directory" if entry.is_dir() else "file",
                }
                for entry in visible[: self.max_entries]
            ],
            "truncated": len(visible) > self.max_entries,
        }

    def read_file(self, path: str) -> ToolResult:
        target = self._resolve(path)
        if not target.is_file():
            raise ToolError("path is not a file")
        try:
            with target.open("r", encoding="utf-8") as stream:
                content = stream.read(self.max_read_chars + 1)
        except (UnicodeError, OSError) as exc:
            raise ToolError(f"cannot read UTF-8 file: {exc}") from exc
        return {
            "path": self._display_path(target),
            "content": content[: self.max_read_chars],
            "truncated": len(content) > self.max_read_chars,
        }

    def write_file(
        self, path: str, content: str, overwrite: bool = False
    ) -> ToolResult:
        if not self.allow_write:
            raise ToolError("write access is disabled; restart with --allow-write")
        target = self._resolve(path)
        if target == self.workspace:
            raise ToolError("path must name a file")
        if not isinstance(content, str):
            raise ToolError("content must be a string")
        if len(content) > MAX_WRITE_CHARS:
            raise ToolError(
                f"content exceeds the {MAX_WRITE_CHARS:,}-character write limit"
            )
        if not isinstance(overwrite, bool):
            raise ToolError("overwrite must be a boolean")
        if not target.parent.is_dir():
            raise ToolError("parent directory does not exist")
        try:
            mode = "w" if overwrite else "x"
            with target.open(mode, encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        except FileExistsError as exc:
            raise ToolError("file exists; set overwrite=true to replace it") from exc
        except OSError as exc:
            raise ToolError(f"cannot write file: {exc}") from exc
        return {
            "path": self._display_path(target),
            "characters": len(content),
        }

    def execute(self, name: str, arguments: Any) -> str:
        """Run one tool and return a JSON success or error envelope."""
        try:
            parsed = json.loads(arguments) if isinstance(arguments, str) else arguments
            if not isinstance(parsed, dict):
                raise ToolError("arguments must be a JSON object")

            operations: dict[str, Callable[..., ToolResult]] = {
                "list_files": self.list_files,
                "read_file": self.read_file,
            }
            if self.allow_write:
                operations["write_file"] = self.write_file

            operation = operations.get(name)
            if operation is None:
                raise ToolError(f"unknown or disabled tool: {name}")
            response = {"ok": True, "result": operation(**parsed)}
        except (ToolError, TypeError, ValueError) as exc:
            response = {"ok": False, "error": str(exc)}

        return json.dumps(response, ensure_ascii=False)
