from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import todo_mcp_server


class TodoMcpServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._original_path = todo_mcp_server.TASKS_PATH
        todo_mcp_server.TASKS_PATH = Path(self._tempdir.name) / "tasks.json"

    def tearDown(self) -> None:
        todo_mcp_server.TASKS_PATH = self._original_path

    def test_add_task_writes_and_returns_task(self) -> None:
        result = todo_mcp_server.add_task("buy milk")

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["title"], "buy milk")
        self.assertIn("created_at", result)

        with todo_mcp_server.TASKS_PATH.open("r", encoding="utf-8") as handle:
            stored = json.load(handle)
        self.assertEqual(stored, [result])

    def test_add_task_assigns_incrementing_ids(self) -> None:
        first = todo_mcp_server.add_task("a")
        second = todo_mcp_server.add_task("b")

        self.assertEqual(first["id"], 1)
        self.assertEqual(second["id"], 2)

    def test_list_tasks_returns_newest_first_and_applies_limit(self) -> None:
        todo_mcp_server.add_task("first")
        todo_mcp_server.add_task("second")
        todo_mcp_server.add_task("third")

        result = todo_mcp_server.list_tasks(limit=1000)

        self.assertEqual([task["title"] for task in result], ["third", "second", "first"])

        limited = todo_mcp_server.list_tasks(limit=2)
        self.assertEqual([task["title"] for task in limited], ["third", "second"])

    def test_list_tasks_returns_empty_when_file_missing(self) -> None:
        self.assertEqual(todo_mcp_server.list_tasks(), [])


if __name__ == "__main__":
    unittest.main()
