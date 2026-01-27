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

Read `.tiki/state/current.json` for `activeIssue` and `currentPhase`.

If no active issue:
```
No active issue. Use `/tiki:execute <issue>` to start execution.
```

### Step 2: Determine Phase to Skip

Parse phase from arguments:

1. **Explicit number**: `/skip-phase 3` - skip phase 3
2. **Current flag**: `/skip-phase --current` - skip current phase from state
3. **No argument**: Default to current in-progress phase

If phase number is ambiguous, show available phases with status and prompt for selection.

### Step 3: Validate Skip Request

Read `.tiki/plans/issue-<N>.json` and validate.

Read `.tiki/prompts/skip-phase/validation-checks.md` for validation rules and error message formats.

### Step 4: Update Plan and State

Read `.tiki/prompts/skip-phase/state-updates.md` for file update instructions and confirmation display format.

### Step 5: Handle Edge Cases

If needed, read `.tiki/prompts/skip-phase/examples-and-edge-cases.md` for guidance on:

- Skipping last phase
- Multiple phase skips
- Missing reason handling

## Notes

- Skipping is permanent for the current execution - use `/tiki:redo-phase` to undo
- Skipped phases are tracked for reporting and review
- Consider using `/tiki:heal` for failed phases before skipping
- Dependencies are warned about but not enforced - skipping may cause downstream failures
