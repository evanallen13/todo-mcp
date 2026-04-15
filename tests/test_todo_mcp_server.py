from __future__ import annotations

from datetime import datetime, timezone
import unittest
from unittest.mock import MagicMock, patch

import todo_mcp_server


def _connection_context(cursor: MagicMock) -> MagicMock:
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False
    return connection


class TodoMcpServerTests(unittest.TestCase):
    def test_add_task_inserts_and_returns_row(self) -> None:
        created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        cursor = MagicMock()
        cursor.fetchone.return_value = (12, "buy milk", created_at)
        connection = _connection_context(cursor)

        with patch.object(todo_mcp_server, "_connect", return_value=connection):
            result = todo_mcp_server.add_task("buy milk")

        self.assertEqual(
            result,
            {"id": 12, "title": "buy milk", "created_at": created_at.isoformat()},
        )
        self.assertEqual(cursor.execute.call_count, 2)
        insert_sql = cursor.execute.call_args_list[1].args[0]
        self.assertIn("INSERT INTO tasks", insert_sql)

    def test_list_tasks_reads_rows_and_applies_limit_bounds(self) -> None:
        created_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
        cursor = MagicMock()
        cursor.fetchall.return_value = [(7, "walk dog", created_at)]
        connection = _connection_context(cursor)

        with patch.object(todo_mcp_server, "_connect", return_value=connection):
            result = todo_mcp_server.list_tasks(limit=1000)

        self.assertEqual(
            result,
            [{"id": 7, "title": "walk dog", "created_at": created_at.isoformat()}],
        )
        self.assertEqual(cursor.execute.call_count, 2)
        list_sql, list_params = cursor.execute.call_args_list[1].args
        self.assertIn("SELECT id, title, created_at", list_sql)
        self.assertEqual(list_params, (500,))
