---
type: prompt
name: tiki:add-todo
description: Add a todo item to the backlog for later tracking. Quick capture of tasks without creating a full GitHub issue.
allowed-tools: Read, Write, Bash
argument-hint: ["description"] [--priority high|medium|low]
---

# Add Todo

Add a quick todo item to your backlog for later tracking.

## Usage

```
/tiki:add-todo
/tiki:add-todo "Fix the login bug later"
/tiki:add-todo "Refactor auth module" --priority high
```

## Instructions

### Step 1: Parse Input

Extract description (in quotes) and --priority flag (high/medium/low, default: medium).
If no description provided, prompt user for one.

### Step 2: Read and Update Todos

Read `.tiki/todos.json` (or create with `{"todos": []}`).
Read `.tiki/prompts/add-todo/todo-format.md` for structure and ID generation.

### Step 3: Save and Confirm

Write updated todos to `.tiki/todos.json`.
Display confirmation:

```
Added {id}: "{description}"
Priority: {priority}

Next steps:
- View todos: /tiki:list-todos
- Add another: /tiki:add-todo "description"
```

## Notes

- Todos stored locally in `.tiki/todos.json` (not synced to GitHub)
- Use `/tiki:list-todos` to view all todos
- Todos can be converted to GitHub issues with `/tiki:list-todos --convert`
