---
type: prompt
name: tiki:redo-phase
description: Re-execute a completed or failed phase. Use when you need to redo work on a specific phase.
allowed-tools: Read, Write, Edit, Bash, Glob
argument-hint: <phase-number> [--cascade] [--issue <n>]
---

# Redo Phase

Reset a phase to pending status so it can be re-executed. Useful when a phase needs to be redone due to changed requirements, discovered issues, or to incorporate improvements.

## Usage

```
/tiki:redo-phase 2
/tiki:redo-phase 2 --cascade        # Also reset dependent phases
/tiki:redo-phase 2 --issue 34       # Specify issue number
```

## Instructions

### Step 1: Parse Arguments

Extract from arguments:
- **Phase number** (required): Which phase to redo
- **Issue number** (optional): Defaults to active issue from `.tiki/state/current.json`
- **--cascade** (optional): Also reset phases that depend on this one

### Step 2: Load Current State

Read `.tiki/state/current.json`:
```json
{
  "activeIssue": 2,
  "currentPhase": 3,
  "status": "in_progress",
  "completedPhases": [1, 2]
}
```

Read `.tiki/plans/issue-{number}.json` to get phase details.

### Step 3: Validate Phase

Check that the phase is valid for redo:

#### Valid States for Redo
- `completed` - Phase finished but needs rework
- `failed` - Phase failed and needs retry (after fixing issues)
- `skipped` - Phase was skipped but now needs to be done

#### Invalid States
- `pending` - Already pending, nothing to redo
- `in_progress` - Cannot redo a phase that's currently running

If invalid:
```
Cannot redo phase 2.

Current status: in_progress
Reason: Phase is currently being executed.

Wait for the phase to complete or use `/tiki:pause` to stop execution.
```

### Step 4: Identify Dependent Phases

Check if any later phases depend on this phase's output.

Dependencies are phases where:
1. They have a higher phase number AND
2. They reference files modified in this phase OR
3. They explicitly list this phase in their `dependencies` array

Example dependency chain:
```
Phase 2: Create user model
Phase 3: Add user routes (depends on Phase 2)
Phase 4: Add user tests (depends on Phase 2 and 3)
```

If redoing Phase 2:
```
## Dependency Analysis

Phase 2 has downstream dependencies:
- Phase 3: Add user routes (depends on Phase 2)
- Phase 4: Add user tests (depends on Phase 2)

Options:
1. Redo Phase 2 only (dependencies keep their current state)
2. Cascade: Also reset Phases 3 and 4 to pending

Use `--cascade` to reset all dependent phases.
```

### Step 5: Reset Phase State

Update the phase in `.tiki/plans/issue-{number}.json`:

#### Before Reset
```json
{
  "number": 2,
  "title": "Create user model",
  "status": "completed",
  "summary": "Created User model with validation",
  "completedAt": "2026-01-10T10:00:00Z"
}
```

#### After Reset
```json
{
  "number": 2,
  "title": "Create user model",
  "status": "pending",
  "summary": null,
  "completedAt": null,
  "redoAt": "2026-01-10T14:00:00Z",
  "redoReason": "User requested redo"
}
```

Fields to clear:
- `status` -> `"pending"`
- `summary` -> `null`
- `completedAt` -> `null`
- `error` -> `null` (if present from failed state)
- `failedAt` -> `null` (if present)
- `skippedAt` -> `null` (if present)

Fields to add:
- `redoAt` - Timestamp of when redo was requested
- `redoReason` - Optional reason (from `--reason "..."` argument)

### Step 6: Update State File

Update `.tiki/state/current.json`:

```json
{
  "activeIssue": 2,
  "currentPhase": 2,
  "status": "in_progress",
  "completedPhases": [1],
  "lastActivity": "2026-01-10T14:00:00Z"
}
```

Key updates:
- Remove the redone phase from `completedPhases`
- If cascading, also remove dependent phases from `completedPhases`
- Update `currentPhase` to the redone phase number
- Update `lastActivity` timestamp

### Step 7: Handle Cascade (if --cascade)

If `--cascade` flag is provided, also reset dependent phases:

```
Resetting Phase 2 and dependent phases...

Phase 2: Create user model
  Status: completed -> pending
  Cleared: summary, completedAt

Phase 3: Add user routes
  Status: completed -> pending
  Cleared: summary, completedAt

Phase 4: Add user tests
  Status: pending (unchanged)

Updated completedPhases: [1]
```

### Step 8: Confirm and Show Next Steps

```
## Phase 2 Reset for Redo

Phase "Create user model" has been reset to pending.

### Changes Made
- Status: completed -> pending
- Cleared: summary, completedAt
- Added: redoAt

### Dependent Phases
- Phase 3: Add user routes (not reset - use --cascade to include)
- Phase 4: Add user tests (not reset - use --cascade to include)

### Next Steps
- Review phase requirements: `/tiki:state`
- Execute from this phase: `/tiki:execute 2 --from 2`
- Or continue full execution: `/tiki:execute 2`
```

## Edge Cases

### Phase Does Not Exist

```
Error: Phase 5 does not exist.

Issue #2 has 3 phases (1-3).

Use `/tiki:state` to see all phases.
```

### Phase is Currently Running

```
Cannot redo Phase 2.

Status: in_progress
The phase is currently being executed.

Options:
- Wait for completion
- Use `/tiki:pause` to stop current execution
- Then retry `/tiki:redo-phase 2`
```

### No Active Issue

If no issue number provided and no active issue:

```
Error: No active issue.

Specify an issue number:
  /tiki:redo-phase 2 --issue 34

Or start working on an issue:
  /tiki:execute 34
```

### All Phases Would Be Reset

When cascading would reset all phases:

```
Warning: Cascading from Phase 1 would reset ALL phases.

This effectively restarts the entire issue execution.

Proceed? This will:
- Reset phases: 1, 2, 3, 4
- Clear all summaries and completion data

Consider using `/tiki:execute 34 --from 1` instead for a fresh start.
```

## Examples

### Example 1: Simple Redo

```
> /tiki:redo-phase 2

Phase 2 "Add user authentication" reset to pending.

Previous status: completed
Previous summary: Added JWT auth middleware

Next: `/tiki:execute 15 --from 2`
```

### Example 2: Redo Failed Phase After Fix

```
> /tiki:redo-phase 3

Phase 3 "Add payment integration" reset to pending.

Previous status: failed
Previous error: Stripe API key not configured

Make sure you've fixed the issue before re-executing.

Next: `/tiki:execute 15 --from 3`
```

### Example 3: Cascade Redo

```
> /tiki:redo-phase 2 --cascade

Resetting Phase 2 and 2 dependent phases...

Reset:
- Phase 2: Create user model (completed -> pending)
- Phase 3: Add user routes (completed -> pending)
- Phase 4: Add user tests (completed -> pending)

Completed phases remaining: [1]

Next: `/tiki:execute 15 --from 2`
```

### Example 4: Redo with Reason

```
> /tiki:redo-phase 2 --reason "Requirements changed - need email field"

Phase 2 "Create user model" reset to pending.

Reason recorded: Requirements changed - need email field

Next: `/tiki:execute 15 --from 2`
```

## File Updates Summary

### .tiki/plans/issue-{number}.json

Update the specific phase object:
```json
{
  "number": 2,
  "status": "pending",
  "summary": null,
  "completedAt": null,
  "redoAt": "2026-01-10T14:00:00Z",
  "redoReason": "User requested redo"
}
```

### .tiki/state/current.json

Update state to reflect the redo:
```json
{
  "activeIssue": 2,
  "currentPhase": 2,
  "status": "in_progress",
  "completedPhases": [1],
  "lastActivity": "2026-01-10T14:00:00Z"
}
```

## Notes

- Redo preserves the original phase content and tasks - only status is reset
- Use `--cascade` carefully as it may reset significant work
- After redo, the phase will be re-executed with fresh context
- Previous summaries are cleared to avoid confusion with new execution
- The `redoAt` timestamp helps track when/why phases were redone
- Consider using `/tiki:heal` first if the phase failed due to a fixable error
