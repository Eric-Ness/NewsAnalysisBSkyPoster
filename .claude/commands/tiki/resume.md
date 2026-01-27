---
type: prompt
name: tiki:resume
description: Resume paused work with full context restoration. Use when continuing work that was previously paused.
allowed-tools: Read, Write, Glob, Bash, Task, Edit, Grep
argument-hint: [issue-number]
---

# Resume

Resume a paused execution by loading saved context and continuing from where work left off.

## Usage

```
/tiki:resume
/tiki:resume 34
```

## Instructions

### Step 1: Find Paused Work

If no issue number provided, check for paused work:

1. Read `.tiki/state/current.json`
2. Look for `status: "paused"`

If issue number provided, verify it has paused state.

If no paused work found:
```
No paused work found.

Use `/tiki:state` to see current status.
Use `/tiki:execute <number>` to start execution.
```

### Step 2: Load Context

Read the saved context from `.tiki/context/issue-N-phase-M.json`:

```json
{
  "issue": { "number": 34, "title": "Add user authentication" },
  "phase": { "number": 2, "title": "Add login endpoint", "content": "..." },
  "pausedAt": "2026-01-10T14:30:00Z",
  "progress": {
    "description": "Implemented POST /api/login, still need to add tests",
    "filesModified": ["src/routes/auth.ts", "src/services/auth.ts"],
    "tasksCompleted": ["Created login route", "Implemented password validation"],
    "tasksRemaining": ["Add unit tests", "Add integration tests"]
  },
  "decisions": ["Used bcrypt for password hashing"],
  "notes": "Auth service needs error handling for edge cases",
  "previousPhaseSummaries": [...]
}
```

### Step 3: Verify File State

Check that the files mentioned in context still exist and haven't been modified unexpectedly:

```bash
git status
```

If there are conflicts or unexpected changes:
```
## Context Conflict

Files have changed since pause:
- src/routes/auth.ts (modified externally)

Options:
1. Continue anyway (may need to reconcile changes)
2. Reset to paused state: `git checkout src/routes/auth.ts`
3. Review changes first: `git diff src/routes/auth.ts`

Continue with resume? [y/n]
```

### Step 4: Display Context Summary

Show the user what was happening:

```
## Resuming Issue #34: Add user authentication

### Paused State
- **Phase:** 2 of 3 - Add login endpoint
- **Paused:** 2 hours ago
- **Reason:** User requested pause

### Progress When Paused
**Completed:**
- Created login route
- Implemented password validation
- Added JWT generation

**Remaining:**
- Add unit tests
- Add integration tests

### Decisions Made
- Used bcrypt for password hashing (industry standard)
- JWT expires in 24 hours

### Notes
Auth service needs error handling for edge cases

### Previous Phases
- Phase 1: Setup auth middleware - Created JWT validation middleware

---
Continuing execution...
```

### Step 5: Update State

Update `.tiki/state/current.json`:
- Set `status: "in_progress"`
- Clear `pausedAt`
- Update `lastActivity`

Update phase status in plan file:
- Set phase `status: "in_progress"`

### Step 6: Continue Execution

Two options:

#### Option A: Continue in Current Context

If the remaining work is small and context allows, continue directly:

```
Continuing Phase 2...

Based on the saved context, I need to:
1. Add unit tests for the login endpoint
2. Add integration tests

[Proceeds with implementation]
```

#### Option B: Spawn Sub-Agent

If the remaining work is substantial, spawn a sub-agent with full context:

```
You are resuming Phase 2 of 3 for Issue #34: Add user authentication

## Project Context
<CLAUDE.md contents>

## Previous Phase Summaries
- Phase 1: Setup auth middleware - Created JWT validation middleware

## Current Phase: Add login endpoint

<original phase content>

## Progress Already Made
The following was completed before pause:
- Created login route at src/routes/auth.ts
- Implemented password validation in src/services/auth.ts
- Added JWT generation

## Remaining Tasks
- Add unit tests
- Add integration tests

## Decisions Already Made
- Used bcrypt for password hashing (industry standard)
- JWT expires in 24 hours

## Notes From Previous Session
Auth service needs error handling for edge cases

## Instructions
1. Continue from where we left off
2. Complete the remaining tasks listed above
3. Run tests to verify everything works
4. Provide a summary when done with "SUMMARY:" prefix
```

### Step 7: Handle Completion

When the resumed phase completes:

1. Update phase to `completed` with summary
2. Delete the context file (no longer needed)
3. Continue to next phase or complete execution

```
Phase 2 complete: Add login endpoint
Summary: Added comprehensive tests for login endpoint, fixed edge case handling

Context file cleaned up.
Continuing to Phase 3...
```

## Context File Format

`.tiki/context/issue-N-phase-M.json`:

```json
{
  "issue": {
    "number": 34,
    "title": "Add user authentication"
  },
  "phase": {
    "number": 2,
    "title": "Add login endpoint",
    "content": "Full phase instructions..."
  },
  "pausedAt": "2026-01-10T14:30:00Z",
  "reason": "User requested pause",
  "progress": {
    "description": "Human-readable summary of progress",
    "filesModified": ["list", "of", "files"],
    "filesCreated": ["new", "files"],
    "tasksCompleted": ["what's", "done"],
    "tasksRemaining": ["what's", "left"]
  },
  "decisions": [
    "Decision 1 with rationale",
    "Decision 2 with rationale"
  ],
  "notes": "Any additional context",
  "previousPhaseSummaries": [
    {
      "number": 1,
      "title": "Phase 1 title",
      "summary": "What phase 1 accomplished"
    }
  ]
}
```

## Edge Cases

### Multiple Paused Issues

If multiple issues are paused, show options:

```
Multiple paused issues found:

| Issue | Phase | Paused |
|-------|-------|--------|
| #34 | 2/3 | 2 hours ago |
| #35 | 1/2 | 1 day ago |

Which would you like to resume?
- `/tiki:resume 34`
- `/tiki:resume 35`
```

### Stale Context

If context is very old (> 7 days):

```
## Stale Context Warning

This work was paused 10 days ago. The codebase may have changed significantly.

Options:
1. Resume anyway (context may be outdated)
2. Start fresh: `/tiki:execute 34 --from 2`
3. Review plan first: `/tiki:state`
```

### Context File Missing

If state shows paused but context file is missing:

```
## Context Lost

Issue #34 is marked as paused but context file is missing.

Options:
1. Start phase fresh: `/tiki:execute 34 --from 2`
2. Review what files were being modified and continue manually
```

## Notes

- Resume is designed to minimize context loss between sessions
- The context file is the source of truth for resuming
- If in doubt, start the phase fresh with `/tiki:execute --from N`
- Clean up context files after successful phase completion
