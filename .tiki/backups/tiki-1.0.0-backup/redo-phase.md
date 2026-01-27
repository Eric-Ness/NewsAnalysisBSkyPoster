---
type: prompt
name: tiki:redo-phase
description: Re-execute a completed or failed phase. Use when you need to redo work on a specific phase.
allowed-tools: Read, Write, Edit, Bash, Glob
argument-hint: <phase-number> [--cascade] [--issue <n>]
---

# Redo Phase

Reset a phase to pending status so it can be re-executed.

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
- **--reason** (optional): Reason for the redo

### Step 2: Load Current State

Read `.tiki/state/current.json` and `.tiki/plans/issue-{number}.json`.

### Step 3: Validate Phase

**Valid states:** `completed`, `failed`, `skipped`
**Invalid states:** `pending` (nothing to redo), `in_progress` (currently running)

### Step 4: Identify Dependent Phases

Find phases that depend on this one (higher number AND reference modified files OR explicit `dependencies` array). Show dependency analysis if found.

### Step 5: Reset Phase State

Update phase in `.tiki/plans/issue-{number}.json`:

- Set `status` to `"pending"`
- Clear: `summary`, `completedAt`, `error`, `failedAt`, `skippedAt`
- Add: `redoAt` (timestamp), `redoReason` (if provided)

### Step 6: Update State File

Update `.tiki/state/current.json`:

- Remove redone phase from `completedPhases`
- Set `currentPhase` to the redone phase number
- Update `lastActivity` timestamp

### Step 7: Handle Cascade

If `--cascade` flag provided, also reset all dependent phases (apply Step 5-6 to each).

### Step 8: Confirm and Show Next Steps

Show summary of changes and suggest: `/tiki:execute {issue} --from {phase}`

## Conditional Prompts

For edge cases (phase not found, no active issue, phase running, cascade warnings) and usage examples, read: `.tiki/prompts/redo-phase/examples-and-edge-cases.md`

## Notes

- Redo preserves phase content - only status is reset
- Use `--cascade` carefully as it may reset significant work
- Consider `/tiki:heal` first if phase failed due to a fixable error
