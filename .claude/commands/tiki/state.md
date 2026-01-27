---
type: prompt
name: tiki:state
description: View current Tiki state including active issues, phase progress, and queue items. Use when checking status, seeing what's in progress, or getting an overview of work.
allowed-tools: Read, Glob, Bash
---

# State

Display the current Tiki state: active issues, phase progress, queue items, and recent activity.

## Usage

```
/tiki:state
```

## Instructions

### Step 1: Check for State Files

Look for Tiki state files:

```
.tiki/
├── state/
│   └── current.json     # Active execution state
├── plans/
│   └── issue-*.json     # All planned issues
├── queue/
│   └── pending.json     # Items needing review
└── context/
    └── *.json           # Saved context for resume
```

### Step 2: Read Current State

If `.tiki/state/current.json` exists, read it:

```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "in_progress",
  "startedAt": "2026-01-10T10:00:00Z",
  "lastActivity": "2026-01-10T11:30:00Z",
  "pausedAt": null
}
```

### Step 3: Read All Plans

Glob for `.tiki/plans/issue-*.json` and read each to get:
- Issue number and title
- Overall status (planned, in_progress, completed)
- Phase progress (e.g., "2 of 5 phases complete")

### Step 4: Check Queue

If `.tiki/queue/pending.json` exists, count pending items.

### Step 5: Check for Paused Work

Look for context files in `.tiki/context/` that indicate paused work.

### Step 6: Display State

Format output like this:

```
## Tiki State

### Active Work
**Issue #34:** Add user authentication
- Status: in_progress
- Progress: Phase 2 of 3 (67%)
- Current phase: Add login endpoint
- Started: 2 hours ago
- Last activity: 15 minutes ago

### Planned Issues
| Issue | Title | Phases | Status |
|-------|-------|--------|--------|
| #34 | Add user authentication | 3 | in_progress |
| #35 | Fix login redirect | 1 | planned |
| #36 | Update docs | 2 | planned |

### Queue
**3 items** pending review
- 1 potential new issue
- 2 questions needing input

### Paused Work
None

---
**Next:** Continue with `/tiki:execute 34` or `/tiki:whats-next` for suggestions
```

## State When Nothing is Active

If no active work:

```
## Tiki State

### Active Work
No active execution.

### Planned Issues
| Issue | Title | Phases | Status |
|-------|-------|--------|--------|
| #35 | Fix login redirect | 1 | planned |
| #36 | Update docs | 2 | planned |

### Queue
Empty

### Paused Work
None

---
**Next:** Start work with `/tiki:execute <issue-number>` or plan a new issue with `/tiki:plan-issue <number>`
```

## State When Nothing Exists

If `.tiki/` folder is empty or doesn't exist:

```
## Tiki State

No Tiki state found. This project hasn't been set up with Tiki yet.

**Get started:**
1. View GitHub issues: `/tiki:get-issue <number>`
2. Plan an issue: `/tiki:plan-issue <number>`
3. Execute the plan: `/tiki:execute <number>`
```

## Current State File Format

`.tiki/state/current.json`:

```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "in_progress",
  "startedAt": "2026-01-10T10:00:00Z",
  "lastActivity": "2026-01-10T11:30:00Z",
  "pausedAt": null,
  "completedPhases": [
    {
      "number": 1,
      "title": "Setup auth middleware",
      "summary": "Created auth middleware with JWT validation",
      "completedAt": "2026-01-10T10:30:00Z"
    }
  ]
}
```

## Notes

- State is read-only - this skill only displays, never modifies
- For detailed phase info, read the plan file directly
- Queue details available via `/tiki:review-queue`
- Use `/tiki:whats-next` for actionable suggestions
