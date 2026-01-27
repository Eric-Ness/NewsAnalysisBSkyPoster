---
type: prompt
name: tiki:discuss-phases
description: Review and adjust phase boundaries interactively. Use when you want to modify, reorder, split, or merge phases in an existing plan.
allowed-tools: Read, Write, Edit, Glob
argument-hint: [issue-number] [--show-deps]
---

# Discuss Phases

Interactive review and adjustment of phase boundaries for a planned issue.

## Instructions

### Step 1: Load Plan

1. If no issue number: read `.tiki/state/current.json` for active issue
2. Read `.tiki/plans/issue-{number}.json`
3. If no plan: prompt to run `/tiki:plan-issue {number}` first

### Step 2: Display Phases

Show phase breakdown with: title, status, priority, files, dependencies, tasks.

```
## Phase Review: Issue #34 - Add user authentication
### Current Phases (3)
**Phase 1: Setup auth middleware** [pending] - Files: src/middleware/auth.ts
**Phase 2: Add login endpoint** [pending] - Dependencies: Phase 1
**Phase 3: Add protected routes** [pending] - Dependencies: Phase 1, 2

What would you like to adjust? (split, merge, reorder, modify, add, remove)
```

### Step 3: Process Adjustments

Supported operations:

- **split** - Divide phase into multiple (renumber, update deps)
- **merge** - Combine phases (merge files/tasks, warn on size)
- **reorder** - Move phase position (validate deps flow forward)
- **modify** - Add/change content (tasks, files, verification)
- **add** - Insert new phase (ask position and details)
- **remove** - Delete phase (handle dependents)

Read `.tiki/prompts/discuss-phases/operations.md` for detailed operation handling and example dialogs.

### Step 4: Validate & Save

After changes: validate deps, check size limits, confirm with user, write to plan file with history entry.

### Step 5: Show Summary

Display updated phase list with change summary and next steps (`/tiki:execute`, `/tiki:audit-plan`).

## Dependency Visualization (--show-deps)

Display ASCII tree showing phase dependencies:
```
Phase 1 (Setup)
├── Phase 2 (Login)
│   └── Phase 3 (Token refresh)
```

## Common Operations

| Command                  | Action                 |
|--------------------------|------------------------|
| "split 2 at task 4"      | Split at specific task |
| "merge 2 and 3"          | Combine phases         |
| "move 3 before 2"        | Reorder                |
| "add tests phase"        | New phase              |
| "remove 4"               | Delete phase           |
| "rename 2 to 'Auth API'" | Rename                 |

## Constraints

- Dependencies flow forward (Phase N depends only on 1..N-1)
- No circular dependencies
- Warn if >10 tasks or >15 files per phase
- Note file conflicts across phases

## Notes

- Completed/in-progress phases cannot be modified (use `/tiki:redo-phase`)
- History tracked in plan file
- Run `/tiki:audit-plan` after major changes
