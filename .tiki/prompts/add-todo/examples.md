# Add Todo Examples

## Example 1: Simple Todo

```
User: /tiki:add-todo "Review PR #42"

Claude: Added todo-001: "Review PR #42"
Priority: medium

Next steps:
- View todos: /tiki:list-todos
- Add another: /tiki:add-todo "description"
```

## Example 2: High Priority Todo

```
User: /tiki:add-todo "Fix production bug in auth" --priority high

Claude: Added todo-002: "Fix production bug in auth"
Priority: high

Next steps:
- View todos: /tiki:list-todos
- Add another: /tiki:add-todo "description"
```

## Example 3: No Argument Provided

```
User: /tiki:add-todo

Claude: What would you like to add to your todo list? Please provide a description.

User: Clean up deprecated API endpoints

Claude: Added todo-003: "Clean up deprecated API endpoints"
Priority: medium

Next steps:
- View todos: /tiki:list-todos
- Add another: /tiki:add-todo "description"
```

## Example 4: Low Priority Todo

```
User: /tiki:add-todo "Update documentation" --priority low

Claude: Added todo-004: "Update documentation"
Priority: low

Next steps:
- View todos: /tiki:list-todos
- Add another: /tiki:add-todo "description"
```

## Error Handling

- **Empty description:** Prompt the user to provide a description
- **Invalid priority:** Default to medium and continue (or warn user)
- **File write error:** Report error and suggest checking `.tiki/` directory permissions
