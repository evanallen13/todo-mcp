from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

TASKS_PATH = Path(os.getenv("TASKS_PATH", "tasks.json"))

_provider = TracerProvider()
_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(_provider)
tracer = trace.get_tracer("todo-mcp")

mcp = FastMCP("todo-mcp")


def _load_tasks() -> list[dict[str, Any]]:
    with tracer.start_as_current_span("load_tasks"):
        if not TASKS_PATH.exists():
            return []
        with TASKS_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def _save_tasks(tasks: list[dict[str, Any]]) -> None:
    with tracer.start_as_current_span("save_tasks"):
        TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TASKS_PATH.open("w", encoding="utf-8") as handle:
            json.dump(tasks, handle, indent=2)


@mcp.tool()
def add_task(title: str) -> dict[str, Any]:
    """Add a task to the todo list."""
    with tracer.start_as_current_span("add_task") as span:
        span.set_attribute("todo.title", title)
        tasks = _load_tasks()
        next_id = max((task["id"] for task in tasks), default=0) + 1
        task = {
            "id": next_id,
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        tasks.append(task)
        _save_tasks(tasks)
        return task


@mcp.tool()
def list_tasks(limit: int = 100) -> list[dict[str, Any]]:
    """Read tasks from the todo list."""
    normalized_limit = max(1, min(limit, 500))
    with tracer.start_as_current_span("list_tasks") as span:
        span.set_attribute("todo.limit", normalized_limit)
        tasks = _load_tasks()
        tasks.sort(key=lambda task: task["created_at"], reverse=True)
        return tasks[:normalized_limit]


if __name__ == "__main__":
    mcp.run()
