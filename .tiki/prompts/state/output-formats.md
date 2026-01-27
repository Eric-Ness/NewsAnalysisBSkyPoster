# State Output Formats

## Full State Display

When active work exists:

```text
## Tiki State

### Active Work
**Issue #34:** Add user authentication
- Status: in_progress
- Progress: Phase 2 of 3 (67%)
- Current phase: Add login endpoint
- Started: 2 hours ago
- Last activity: 15 minutes ago

### Context Budget (Next Phase)
{Include if context-budget.md was loaded}

### Active Release
{Include if release-context.md was loaded}

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

## State When Nothing Active

```text
## Tiki State

### Active Work
No active execution.

### Active Release
None

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

When `.tiki/` folder is empty or doesn't exist:

```text
## Tiki State

No Tiki state found. This project hasn't been set up with Tiki yet.

**Get started:**
1. View GitHub issues: `/tiki:get-issue <number>`
2. Plan an issue: `/tiki:plan-issue <number>`
3. Execute the plan: `/tiki:execute <number>`
```

## State File Reference

`.tiki/state/current.json` structure:

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
