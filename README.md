# todo-mcp

MCP server with two tools:

- `add_task(title)` to append a todo task to a JSON file
- `list_tasks(limit=100)` to read tasks from the JSON file

The server also emits OpenTelemetry spans for loading, saving, and reading tasks.

## Run

Optionally set the path to the tasks JSON file (defaults to `tasks.json` in the current directory):

```bash
export TASKS_PATH="tasks.json"
```

Start the MCP server:

```bash
python todo_mcp_server.py
```
