# Todo Actions: Complete and Delete

Handle --complete and --delete operations on todos.

## ID Normalization

Support both `todo-001` and numeric `1` formats:
```javascript
function normalizeId(input) {
  if (/^\d+$/.test(input)) {
    return `todo-${input.padStart(3, '0')}`;
  }
  return input;
}
```

## --complete <id>

Mark a todo as completed.

1. Normalize ID, find todo in `data.todos`
2. If not found: error with available IDs
3. If already completed: note and skip
4. Update: `todo.status = "completed"`, `todo.completedAt = new Date().toISOString()`
5. Write to `.tiki/todos.json`
6. Display: `Completed: [todo-001] "Description"`

## --delete <id>

Remove todo permanently.

1. Normalize ID, find todo index
2. If not found: error with available IDs
3. **Without --force:** Ask confirmation:
   ```
   Are you sure you want to delete [todo-001] "Description"?
   This action cannot be undone.
   Reply with "yes" to confirm, or anything else to cancel.
   ```
   If not confirmed: `Cancelled: Todo [todo-001] was NOT deleted.`
4. **With --force:** Skip confirmation
5. Remove: `data.todos.splice(todoIndex, 1)`
6. Write to `.tiki/todos.json`
7. Display: `Deleted: [todo-001] "Description"`

## Error: ID Not Found

```
Error: Todo [todo-999] not found.

Available todos:
- todo-001: Fix the login bug (pending)
- todo-002: Update README (completed)

Tip: Use full ID (todo-001) or just the number (1).
```

## Error: Invalid ID Format

```
Error: Invalid ID format "abc123".

Expected formats:
- Full ID: todo-001, todo-042
- Numeric shorthand: 1, 42
```
