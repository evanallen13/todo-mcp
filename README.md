# todo-mcp

MCP server with two tools:

- `add_task(title)` to write a todo task to PostgreSQL
- `list_tasks(limit=100)` to read tasks from PostgreSQL

The server also emits OpenTelemetry spans for table setup, task inserts, and task reads.

## Run

Set your PostgreSQL connection string:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/postgres"
```

Start the MCP server:

```bash
python todo_mcp_server.py
```
