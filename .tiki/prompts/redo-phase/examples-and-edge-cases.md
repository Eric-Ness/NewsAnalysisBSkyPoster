# Redo Phase: Examples and Edge Cases

Reference this document when handling edge cases or showing usage examples for the redo-phase command.

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
