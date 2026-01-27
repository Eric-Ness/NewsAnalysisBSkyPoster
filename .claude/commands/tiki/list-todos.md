---
type: prompt
name: tiki:list-todos
description: View and manage todo items in the backlog. Supports filtering by status and actions like complete, convert to issue, and delete.
allowed-tools: Read, Write, Bash, Glob
argument-hint: [--pending] [--completed] [--all] [--complete <id>] [--convert <id>] [--delete <id>] [--force]
---

# List Todos

View and manage todos in your backlog.

## Arguments

**Filter Flags:** `--pending`, `--completed`, `--all` (default)

**Action Flags:**

- `--complete <id>` - Mark todo as complete
- `--convert <id>` - Convert to GitHub issue
- `--delete <id>` - Remove permanently (use `--force` to skip confirmation)

**ID Format:** Both `todo-001` and `1` are valid.

## Instructions

### Step 1: Read Todos

```bash
cat .tiki/todos.json 2>/dev/null || echo '{"todos": []}'
```

### Step 2: Handle Actions (if any)

**If `--complete` or `--delete` specified:**
Read `.tiki/prompts/list-todos/actions.md` and follow instructions.

**If `--convert` specified:**
Read `.tiki/prompts/list-todos/convert-to-issue.md` and follow instructions.

### Step 3: Apply Filter

```javascript
let filtered = data.todos;
if (args.includes('--pending')) filtered = data.todos.filter(t => t.status === 'pending');
else if (args.includes('--completed')) filtered = data.todos.filter(t => t.status === 'completed');
```

### Step 4: Display

**Empty state:**
```
## Todos

No todos found.

Get started: /tiki:add-todo "Your task description"
```

**With todos:**
```
## Todos

### Pending (N)
1. [todo-001] Description (priority priority)

### Completed (N)
2. [todo-002] Description (completed Xh ago)

---

**Summary:** N total | N pending | N completed

**Actions:**
- Complete: `/tiki:list-todos --complete <id>`
- Convert: `/tiki:list-todos --convert <id>`
- Delete: `/tiki:list-todos --delete <id>`
```

**Time formatting:**

- <1h: "Xm ago"
- <24h: "Xh ago"
- <7d: "Xd ago"
- Older: "Jan 10"

## Error Handling

**File read error:**
```
Error: Could not read todos file.
Try /tiki:add-todo to initialize.
```
