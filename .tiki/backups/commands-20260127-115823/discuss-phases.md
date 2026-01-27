---
type: prompt
name: tiki:discuss-phases
description: Review and adjust phase boundaries interactively. Use when you want to modify, reorder, split, or merge phases in an existing plan.
allowed-tools: Read, Write, Edit, Glob
argument-hint: [issue-number] [--show-deps]
---

# Discuss Phases

Interactive review and adjustment of phase boundaries for a planned issue.

## Usage

```
/tiki:discuss-phases
/tiki:discuss-phases 34
/tiki:discuss-phases 34 --show-deps
```

## Instructions

### Step 1: Load the Plan

If no issue number provided, check for active plan:

1. Read `.tiki/state/current.json` to find active issue
2. Read `.tiki/plans/issue-{number}.json`

If no plan found:
```
No plan found for issue #{number}.

Use `/tiki:plan-issue {number}` to create a plan first.
```

### Step 2: Display Current Phases

Show the current phase breakdown in a clear format:

```
## Phase Review: Issue #34 - Add user authentication

### Current Phases (3)

**Phase 1: Setup auth middleware** [pending]
- Priority: high
- Files: src/middleware/auth.ts, src/types/auth.ts
- Dependencies: none
- Tasks: Create middleware, define types, export functions

**Phase 2: Add login endpoint** [pending]
- Priority: high
- Files: src/routes/auth.ts, src/services/auth.ts
- Dependencies: Phase 1
- Tasks: Implement /api/login, validate credentials, return JWT

**Phase 3: Add protected routes** [pending]
- Priority: medium
- Files: src/routes/user.ts
- Dependencies: Phase 1, 2
- Tasks: Apply auth middleware, handle 401 responses

---
**What would you like to adjust?**
- Split a phase: "split 2 into login and token refresh"
- Merge phases: "merge 2 and 3"
- Reorder: "move phase 3 before phase 2"
- Modify: "add rate limiting to phase 2"
- Add phase: "add a phase for password reset"
- Remove phase: "remove phase 3"
```

### Step 3: Process User Adjustments

Based on user input, perform the requested operation:

#### Split a Phase

User: "split phase 2 into login and token refresh"

1. Read the phase content
2. Create two new phases with split content
3. Renumber subsequent phases
4. Update dependencies

```
Splitting Phase 2...

**New Phase 2: Add login endpoint**
- Files: src/routes/auth.ts
- Tasks: Implement /api/login, validate credentials

**New Phase 3: Add token refresh**
- Files: src/routes/auth.ts, src/services/token.ts
- Dependencies: Phase 2
- Tasks: Implement /api/refresh, validate refresh tokens

Phase 4 (was 3): Add protected routes
- Dependencies updated: Phase 1, 2, 3

Save changes? [Yes/No]
```

#### Merge Phases

User: "merge phases 2 and 3"

1. Combine content from both phases
2. Merge file lists
3. Take earliest dependencies
4. Renumber subsequent phases

```
Merging Phases 2 and 3...

**New Phase 2: Add login and protected routes**
- Files: src/routes/auth.ts, src/services/auth.ts, src/routes/user.ts
- Dependencies: Phase 1
- Tasks: Combined from both phases

Warning: Merged phase has 8 tasks and 4 files - verify it fits in one context window.

Save changes? [Yes/No]
```

#### Reorder Phases

User: "move phase 3 to phase 1"

1. Validate the move doesn't break dependencies
2. Renumber phases
3. Update all dependency references

```
Reordering phases...

Before:
1. Setup auth middleware
2. Add login endpoint
3. Add protected routes

After:
1. Add protected routes (was 3)
2. Setup auth middleware (was 1)
3. Add login endpoint (was 2)

Error: Cannot move Phase 3 to position 1 - it depends on Phase 1 and 2.

Suggested alternatives:
- Move Phase 2 to position 3 instead
- Remove dependencies from Phase 3 first
```

#### Modify a Phase

User: "add rate limiting to phase 2"

1. Update the phase content
2. Add new files if needed
3. Extend verification steps

```
Updating Phase 2...

Added to Phase 2:
- Task: "Implement rate limiting for login endpoint"
- File: src/middleware/rateLimit.ts
- Verification: "Rate limiting blocks after 5 failed attempts"

Save changes? [Yes/No]
```

#### Add a Phase

User: "add a phase for password reset"

1. Determine appropriate position
2. Create new phase with user-provided details
3. Renumber subsequent phases

```
Adding new phase...

Where should this phase go?
- After Phase 2 (before protected routes)
- After Phase 3 (at the end)

User: "after phase 3"

**New Phase 4: Add password reset**
- Priority: medium
- Files: [to be determined]
- Dependencies: Phase 1, 2

Please provide more details:
- What files will this phase modify?
- What are the main tasks?
```

#### Remove a Phase

User: "remove phase 3"

1. Check for dependent phases
2. Remove the phase
3. Renumber subsequent phases
4. Update dependencies

```
Removing Phase 3...

Warning: Phase 4 depends on Phase 3.

Options:
1. Remove Phase 3 and update Phase 4 dependencies to [1, 2]
2. Remove Phase 3 and Phase 4
3. Cancel

Which option? [1/2/3]
```

### Step 4: Validate Changes

After any modification, validate the plan:

```
Validating updated plan...

✓ 4 phases defined
✓ Dependencies valid
✓ No circular dependencies
✓ File conflicts: none
⚠ Phase 2 has 9 tasks - close to limit

Plan updated successfully.
```

### Step 5: Save Changes

Write the updated plan to `.tiki/plans/issue-{number}.json`:

```json
{
  "issue": { ... },
  "created": "2026-01-10T10:00:00Z",
  "modified": "2026-01-10T14:30:00Z",
  "status": "planned",
  "phases": [ ... updated phases ... ],
  "history": [
    {
      "action": "split",
      "phase": 2,
      "timestamp": "2026-01-10T14:30:00Z",
      "description": "Split into login and token refresh"
    }
  ]
}
```

### Step 6: Show Updated Summary

```
## Updated Plan: Issue #34

**Phases:** 4 (was 3)
**Changes:** Split Phase 2 into login and token refresh

### Phase 1: Setup auth middleware [pending]
### Phase 2: Add login endpoint [pending]
### Phase 3: Add token refresh [pending] (new)
### Phase 4: Add protected routes [pending]

---
Ready to execute? Use `/tiki:execute 34`
Run audit first? Use `/tiki:audit-plan 34`
More adjustments? Continue describing changes.
```

## Dependency Visualization

With `--show-deps` flag, display dependency graph:

```
## Dependency Graph: Issue #34

Phase 1 (Setup)
├── Phase 2 (Login)
│   └── Phase 3 (Token refresh)
│       └── Phase 4 (Protected routes)
└── Phase 4 (Protected routes)

Legend:
→ depends on
* can run in parallel with previous
```

## Common Operations

| Command | What it does |
|---------|--------------|
| "split 2 at task 4" | Split phase at specific task |
| "merge 2 and 3" | Combine two phases |
| "move 3 before 2" | Reorder phases |
| "add tests phase" | Add new phase |
| "remove 4" | Remove a phase |
| "rename 2 to 'Auth API'" | Rename a phase |
| "add file to 2" | Add file to phase |
| "change priority of 3 to high" | Update priority |

## Constraints

When making changes, enforce these rules:

1. **Dependencies must flow forward** - Phase N can only depend on phases 1 to N-1
2. **No circular dependencies** - A cannot depend on B if B depends on A
3. **Phase size limits** - Warn if > 10 tasks or > 15 files
4. **File conflict awareness** - Note when multiple phases modify same files

## Notes

- Changes are saved immediately after confirmation
- A history of modifications is kept in the plan file
- Use `/tiki:audit-plan` after major changes to verify plan integrity
- Completed or in-progress phases cannot be modified (use `/tiki:redo-phase` first)
- The goal is to help users fine-tune plans before execution
