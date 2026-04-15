from __future__ import annotations

import os
from typing import Any

import psycopg
from mcp.server.fastmcp import FastMCP
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)

_provider = TracerProvider()
_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(_provider)
tracer = trace.get_tracer("todo-mcp")

mcp = FastMCP("todo-mcp")


def _connect() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL)


def _ensure_tasks_table(connection: psycopg.Connection) -> None:
    with tracer.start_as_current_span("ensure_tasks_table"):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        connection.commit()


@mcp.tool()
def add_task(title: str) -> dict[str, Any]:
    """Add a task to the todo list."""
    with tracer.start_as_current_span("add_task") as span:
        span.set_attribute("todo.title", title)
        with _connect() as connection:
            _ensure_tasks_table(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (title)
                    VALUES (%s)
                    RETURNING id, title, created_at
                    """,
                    (title,),
                )
                task_id, task_title, created_at = cursor.fetchone()
            connection.commit()
        return {"id": task_id, "title": task_title, "created_at": created_at.isoformat()}


@mcp.tool()
def list_tasks(limit: int = 100) -> list[dict[str, Any]]:
    """Read tasks from the todo list."""
    normalized_limit = max(1, min(limit, 500))
    with tracer.start_as_current_span("list_tasks") as span:
        span.set_attribute("todo.limit", normalized_limit)
        with _connect() as connection:
            _ensure_tasks_table(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, created_at
                    FROM tasks
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (normalized_limit,),
                )
                rows = cursor.fetchall()
        return [
            {"id": task_id, "title": title, "created_at": created_at.isoformat()}
            for task_id, title, created_at in rows
        ]


if __name__ == "__main__":
    mcp.run()
