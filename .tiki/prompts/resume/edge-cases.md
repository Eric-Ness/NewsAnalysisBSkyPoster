# Resume: Edge Cases

Reference this document when handling edge cases during resume operations.

## Multiple Paused Issues

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

## Stale Context Warning

If context is very old (> 7 days):

```
## Stale Context Warning

This work was paused 10 days ago. The codebase may have changed significantly.

Options:
1. Resume anyway (context may be outdated)
2. Start fresh: `/tiki:execute 34 --from 2`
3. Review plan first: `/tiki:state`
```

Calculate staleness by comparing `pausedAt` timestamp to current time.

## Context File Missing

If state shows paused but context file is missing:

```
## Context Lost

Issue #34 is marked as paused but context file is missing.

Options:
1. Start phase fresh: `/tiki:execute 34 --from 2`
2. Review what files were being modified and continue manually
```

## Context File Format Reference

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

## Issue Number Mismatch

If user provides issue number that does not match paused state:

```
Issue #35 is not currently paused.

Currently paused: Issue #34 (Phase 2)

Did you mean:
- `/tiki:resume 34` - Resume paused work
- `/tiki:execute 35` - Start new execution
```
