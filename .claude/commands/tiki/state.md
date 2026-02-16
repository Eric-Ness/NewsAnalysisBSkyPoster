---
type: prompt
name: tiki:state
description: View current Tiki state including active issues, phase progress, and queue items. Use when checking status, seeing what's in progress, or getting an overview of work.
allowed-tools: Read, Glob, Bash
---

# State

Display current Tiki state: active issues, phase progress, queue items, and recent activity.

## Usage

```
/tiki:state
```

## Instructions

### Step 1: Check State Files

Look for Tiki state files:

- `.tiki/state/current.json` - Active execution state
- `.tiki/plans/issue-*.json` - All planned issues
- `.tiki/queue/pending.json` - Items needing review
- `.tiki/context/*.json` - Saved context for resume

### Step 2: Read Current State

If `.tiki/state/current.json` exists, determine the state format version:

**Detecting v2 format:** Check if `version` field equals 2 OR if `activeExecutions` array exists.

**For v2 format:**
- Extract `activeExecutions` array - each entry contains: id, issue, issueTitle, currentPhase, totalPhases, status, startedAt, pausedAt, completedPhases, failedPhase, errorMessage
- Extract `executionHistory` array for archived executions count
- Note: v1 fields (activeIssue, currentPhase, status at root level) may still exist for backward compatibility but activeExecutions is the source of truth

**For v1 format (no version field or version=1):**
- Extract: activeIssue, currentPhase, status, startedAt, lastActivity, pausedAt, completedPhases
- This is the legacy single-execution format

### Step 3: Read All Plans

Glob for `.tiki/plans/issue-*.json` and read each to get:
- Issue number and title
- Overall status (planned, in_progress, completed)
- Phase progress (e.g., "2 of 5 phases complete")

### Step 4: Check Queue and Paused Work

- If `.tiki/queue/pending.json` exists, count pending items
- Look for context files in `.tiki/context/` indicating paused work

### Step 5: Check Release Context (Conditional)

If there's an active issue, check if it's part of any release.
Read `.tiki/prompts/state/release-context.md` for lookup logic and display format.

### Step 6: Estimate Context Budget (Conditional)

If there's an active issue with a plan, estimate context budget for next phase.
Read `.tiki/prompts/state/context-budget.md` for estimation formula and thresholds.

### Step 7: Display State

Format output based on current state and version.
Read `.tiki/prompts/state/output-formats.md` for display templates.

**For v2 multi-execution format:**
- Display all active executions with format: "Execution #N: Issue #X - Phase Y/Z (status)"
- Show each execution's status: executing, paused, failed
- If executionHistory has entries, show: "History: N archived executions"
- Failed executions should show error message
- Paused executions should show pause reason if available

**For v1 single-execution format:**
- Continue using the existing display format from output-formats.md

## Notes

- State is read-only - this command only displays, never modifies
- For detailed phase info, read the plan file directly
- Queue details available via `/tiki:review-queue`
- Use `/tiki:whats-next` for actionable suggestions
