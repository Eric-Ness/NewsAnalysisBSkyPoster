# Skip Phase: State Updates

Reference this document when updating files after a skip is validated.

## Update Plan File

Update `.tiki/plans/issue-<N>.json` to mark phase as skipped:

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

Fields to set:
- `status`: "skipped"
- `skippedAt`: ISO timestamp
- `skipReason`: User-provided reason or "No reason provided"

## Update State File

Update `.tiki/state/current.json`:

### If skipped phase was current, advance to next pending phase:

```json
{
  "activeIssue": 34,
  "currentPhase": 3,
  "status": "in_progress",
  "lastActivity": "2026-01-10T14:30:00Z"
}
```

### If no more pending phases, mark as completed:

```json
{
  "activeIssue": 34,
  "currentPhase": null,
  "status": "completed",
  "completedAt": "2026-01-10T14:30:00Z"
}
```

## Confirmation Display

```
Phase 2 skipped.

**Issue #34**: Add user authentication
**Phase 2**: Add authentication
**Reason**: Already implemented manually
**Skipped at**: 2026-01-10 14:30:00

Next: Phase 3 - Add user dashboard

Continue execution with `/tiki:execute 34` or `/tiki:execute 34 --from 3`
```

## File Updates Summary

| File | Update |
|------|--------|
| `.tiki/plans/issue-<N>.json` | Set phase status to `skipped`, add `skippedAt` and `skipReason` |
| `.tiki/state/current.json` | Update `currentPhase` to next pending, update `lastActivity` |
