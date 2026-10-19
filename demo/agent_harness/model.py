"""HTTP adapter for Ollama's native chat API."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ModelError(RuntimeError):
    """The model server failed or returned an invalid response."""


class OllamaClient:
    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
    ) -> None:
        if not model.strip():
            raise ValueError("model must not be empty")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "stream": False,
                "options": {"temperature": 0},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = json.load(response)
        except HTTPError as exc:
            detail = exc.read(500).decode("utf-8", errors="replace")
            raise ModelError(f"Ollama HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError) as exc:
            raise ModelError(f"Cannot reach Ollama at {self.base_url}: {exc}") from exc
        except (ValueError, UnicodeError) as exc:
            raise ModelError(f"Ollama returned invalid JSON: {exc}") from exc

        if not isinstance(body, dict) or not isinstance(body.get("message"), dict):
            raise ModelError("Ollama response has no message object")
        return body["message"]
