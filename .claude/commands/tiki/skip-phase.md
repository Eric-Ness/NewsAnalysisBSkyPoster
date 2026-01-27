---
type: prompt
name: tiki:skip-phase
description: Skip a phase during execution. Use when a phase is blocked, not needed, or you want to move forward without completing it.
allowed-tools: Read, Write, Edit
argument-hint: [phase-number] [--reason "..."] [--current]
---

# Skip Phase

Skip a phase during issue execution, marking it as skipped and advancing to the next phase.

## Usage

```
/tiki:skip-phase
/tiki:skip-phase 2
/tiki:skip-phase 2 --reason "Already implemented manually"
/tiki:skip-phase --current
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<number>` | Phase number to skip (optional if only one valid phase) |
| `--reason` | Reason for skipping (optional but recommended) |
| `--current` | Skip the current in-progress phase |

## Instructions

### Step 1: Identify Active Issue

Read `.tiki/state/current.json` to get the active issue:

```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "in_progress"
}
```

If no active issue:
```
No active issue. Use `/tiki:execute <issue>` to start execution.
```

### Step 2: Determine Phase to Skip

Parse the phase number from arguments:

1. **Explicit number**: `/skip-phase 3` - skip phase 3
2. **Current flag**: `/skip-phase --current` - skip current phase from state
3. **No argument**: Skip current in-progress phase

If phase number is ambiguous or missing:
```
Which phase would you like to skip?

Current phases for Issue #34:
  1. Setup project structure [completed]
  2. Add authentication [in_progress] <-- current
  3. Add user dashboard [pending]
  4. Write tests [pending]

Usage: /tiki:skip-phase <number> or /tiki:skip-phase --current
```

### Step 3: Validate Skip Request

Read `.tiki/plans/issue-<N>.json` and validate:

#### Check 1: Phase Exists

```
Error: Phase 5 does not exist.

Issue #34 has 4 phases. Valid phase numbers: 1-4
```

#### Check 2: Phase is Skippable

A phase can only be skipped if its status is `pending` or `in_progress`.

```
Error: Cannot skip Phase 1 - it is already completed.

Phase statuses:
  1. Setup project structure [completed] - cannot skip
  2. Add authentication [in_progress] - can skip
  3. Add user dashboard [pending] - can skip
```

#### Check 3: Dependency Warning

If other phases depend on this phase, warn but allow skip:

```
Warning: Phase 2 has dependents.

The following phases depend on Phase 2:
  - Phase 3: Add user dashboard (depends on auth)
  - Phase 4: Write tests (depends on auth)

Skipping may cause these phases to fail.

Continue? (y/n)
```

### Step 4: Update Plan File

Update `.tiki/plans/issue-<N>.json`:

```json
{
  "phases": [
    {
      "number": 2,
      "title": "Add authentication",
      "status": "skipped",
      "skippedAt": "2026-01-10T14:30:00Z",
      "skipReason": "Already implemented manually"
    }
  ]
}
```

### Step 5: Update State

Update `.tiki/state/current.json`:

If skipped phase was current, advance to next pending phase:

```json
{
  "activeIssue": 34,
  "currentPhase": 3,
  "status": "in_progress",
  "lastActivity": "2026-01-10T14:30:00Z"
}
```

If no more pending phases, mark as completed:

```json
{
  "activeIssue": 34,
  "currentPhase": null,
  "status": "completed",
  "completedAt": "2026-01-10T14:30:00Z"
}
```

### Step 6: Confirm Skip

Display confirmation:

```
Phase 2 skipped.

**Issue #34**: Add user authentication
**Phase 2**: Add authentication
**Reason**: Already implemented manually
**Skipped at**: 2026-01-10 14:30:00

Next: Phase 3 - Add user dashboard

Continue execution with `/tiki:execute 34` or `/tiki:execute 34 --from 3`
```

## Edge Cases

### Skipping Last Phase

If skipping the final phase:

```
Phase 4 skipped.

All phases complete for Issue #34:
  1. Setup project structure [completed]
  2. Add authentication [completed]
  3. Add user dashboard [completed]
  4. Write tests [skipped]

Issue execution complete. Review with `/tiki:state`.
```

### Skipping Multiple Phases

To skip multiple phases, run the command multiple times:

```
/tiki:skip-phase 2
/tiki:skip-phase 3
```

Or skip a range (if supported):
```
Skipping phases 2-3 is not directly supported.
Please skip one phase at a time to ensure intentional progression.
```

### No Reason Provided

If no reason provided, prompt but don't require:

```
No skip reason provided.

Tip: Add a reason for future reference:
  /tiki:skip-phase 2 --reason "Already done manually"

Proceeding without reason...

Phase 2 skipped.
```

## Examples

### Example 1: Skip Current Phase

```
> /tiki:skip-phase --current

Skipping Phase 2: Add authentication

Phase 2 skipped.

**Reason**: No reason provided
**Next**: Phase 3 - Add user dashboard

Continue with `/tiki:execute 34`.
```

### Example 2: Skip with Reason

```
> /tiki:skip-phase 3 --reason "Feature deprioritized for MVP"

Skipping Phase 3: Add user dashboard

Phase 3 skipped.

**Reason**: Feature deprioritized for MVP
**Next**: Phase 4 - Write tests

Continue with `/tiki:execute 34`.
```

### Example 3: Skip Failed Phase

```
> /tiki:skip-phase 2

Phase 2 is marked as failed.

Error: TypeScript compilation error in src/auth.ts

Options:
1. Skip anyway (mark as skipped, ignore error)
2. Use /tiki:heal to attempt automatic fix
3. Cancel

> 1

Phase 2 skipped (was failed).

**Reason**: No reason provided
**Next**: Phase 3 - Add user dashboard

Note: The error in Phase 2 was not resolved. Dependent phases may fail.
```

### Example 4: Cannot Skip Completed Phase

```
> /tiki:skip-phase 1

Error: Cannot skip Phase 1 - it is already completed.

Completed phases cannot be skipped. If you need to redo this phase, use:
  /tiki:redo-phase 1
```

## File Updates Summary

| File | Update |
|------|--------|
| `.tiki/plans/issue-<N>.json` | Set phase status to `skipped`, add `skippedAt` and `skipReason` |
| `.tiki/state/current.json` | Update `currentPhase` to next pending, update `lastActivity` |

## Integration with Other Skills

- **`/tiki:execute`**: After skipping, use `/tiki:execute` to continue from next phase
- **`/tiki:heal`**: Use heal instead of skip for failed phases you want to fix
- **`/tiki:redo-phase`**: Use redo to repeat a completed or skipped phase
- **`/tiki:state`**: View current status including skipped phases
- **`/tiki:pause`**: Pause instead of skip if you want to return later

## Notes

- Skipping is permanent for the current execution - use `/tiki:redo-phase` to undo
- Skipped phases are tracked for reporting and review
- Consider using `/tiki:heal` for failed phases before skipping
- Dependencies are warned about but not enforced - skipping may cause downstream failures
