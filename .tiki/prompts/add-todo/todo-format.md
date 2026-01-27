# Todo Object Format

## Structure

```json
{
  "id": "todo-001",
  "description": "Fix the login bug later",
  "status": "pending",
  "priority": "medium",
  "createdAt": "2026-01-17T10:30:00Z",
  "completedAt": null,
  "convertedToIssue": null
}
```

## Field Descriptions

| Field | Description |
|-------|-------------|
| `id` | Auto-incrementing ID (todo-001, todo-002, etc.) |
| `description` | The task description provided by the user |
| `status` | Always starts as "pending" |
| `priority` | "high", "medium", or "low" (defaults to "medium") |
| `createdAt` | ISO 8601 timestamp when created |
| `completedAt` | null (set when completed) |
| `convertedToIssue` | null (set when converted to GitHub issue) |

## ID Generation

Generate auto-incrementing ID in format `todo-NNN`:

1. Read existing todos to find highest ID number
2. Increment by 1 for new todo
3. If no todos exist, start with `todo-001`
4. Pad number to 3 digits (001, 002, 003...)

```javascript
const maxId = data.todos.reduce((max, t) => {
  const num = parseInt(t.id.replace('todo-', ''), 10);
  return num > max ? num : max;
}, 0);
const nextId = `todo-${String(maxId + 1).padStart(3, '0')}`;
```

## Priority Parsing

```
--priority high   -> high
--priority medium -> medium
--priority low    -> low
(no flag)         -> medium (default)
```

## File Structure

Todos stored in `.tiki/todos.json`:

```json
{
  "todos": [
    { "id": "todo-001", ... },
    { "id": "todo-002", ... }
  ]
}
```

Create file with empty array if it does not exist.
