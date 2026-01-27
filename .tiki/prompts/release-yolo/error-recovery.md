# Error Recovery

Load this prompt when all automatic recovery attempts have failed.

## Recovery Options

Present to user:

```text
### Recovery Options

1. **Manual fix** - Pause YOLO, fix manually, then `/tiki:release-yolo {version} --continue`
2. **Skip issue** - Mark as failed and continue with remaining issues
3. **Abort YOLO** - Stop execution entirely

Enter choice:
```

Use AskUserQuestion for recovery choice.

## Option 1: Manual Fix

- Set yoloState.status to "paused"
- Set yoloState.pauseReason to "manual_intervention"
- Save state
- Display resume instructions:

```text
## YOLO Paused

State saved. After fixing the issue manually:
  /tiki:release-yolo {version} --continue

Current position:
- Issue: #{number} - {title}
- Phase: {currentPhase}/{totalPhases}
```

Exit execution.

## Option 2: Skip Issue

- Add issue to failedIssues array with error details
- Log error to errorHistory
- Continue to next issue

```javascript
yoloState.failedIssues.push(issue.number);
yoloState.errorHistory.push({
  issue: issue.number,
  phase: currentPhase,
  error: errorMessage,
  timestamp: new Date().toISOString(),
  resolution: 'skipped'
});
```

Display:

```text
Issue #{number} marked as failed. Continuing with remaining issues...
```

## Option 3: Abort

- Set yoloState.status to "failed"
- Save state
- Display summary and exit

```text
## YOLO Aborted

Execution aborted. {completedCount}/{totalCount} issues completed.

Completed issues:
{List completed issues}

To retry:
  /tiki:release-yolo {version} --from {failedIssueNumber}
```

## Edge Cases

### State File Corrupted

```text
## YOLO State Corrupted

Options:
1. **Start fresh** - Delete state and start new YOLO
2. **Restore** - Attempt to reconstruct state from release file
3. **Cancel** - Exit without changes
```

### Concurrent YOLO Execution

```text
## YOLO Already Running

A YOLO execution is already in progress for release {version}.

Options:
1. **Continue existing** - Resume the in-progress execution
2. **Restart** - Abort current and start fresh
3. **Cancel** - Exit without changes
```
