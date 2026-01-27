# Resume YOLO Execution

Load this prompt when --continue flag is provided.

## Load Saved State

```bash
if [ -f ".tiki/state/yolo.json" ]; then
  cat ".tiki/state/yolo.json"
else
  echo "NO_YOLO_STATE"
fi
```

### If No Saved State

```text
## No YOLO State Found

No paused YOLO execution to continue.

To start a new YOLO execution:
  /tiki:release-yolo <version>

To see available releases:
  /tiki:release-status
```

Exit execution.

### If Saved State Exists

Extract from state:
- Release version
- Current position (issue and phase)
- Completed issues
- Flags from original invocation

Override with any new flags provided (e.g., `--skip-verify` can be added on continue).

## Display Resume Information

```text
## Resuming YOLO Execution

Release: {version}
Started: {startedAt}
Progress: {completedIssues.length}/{totalIssues} issues complete

### Completed Issues
{For each completed issue:}
- #{number}: {title}

### Resuming From
Issue #{currentIssue}: {title}
Phase: {currentPhase}/{totalPhases}

Continue? [Y/n]
```

Use AskUserQuestion to confirm.

## State Mismatch Handling

If an issue in saved state was removed from release:

```text
## State Mismatch

Issue #{number} in saved state is no longer in release {version}.

Options:
1. **Continue** - Skip missing issue and continue
2. **Cancel** - Exit and investigate

Enter choice:
```

## Resume Position

After confirmation, skip to the issue processing loop at the saved position:
- Set issueIndex to the position of currentIssue in issueOrder
- If currentPhase is set, resume from that phase via `--from` flag

## Verification Pause Resume

If paused during verification (pauseReason === 'verification_pending'):

```text
## Resuming Verification

{autoVerifiedCount} requirements auto-verified.
{pendingManualCount} requirements pending manual verification.

Continue with manual verification? [Y/n]
```

Resume verification flow from saved position.
