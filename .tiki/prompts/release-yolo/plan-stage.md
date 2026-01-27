# Plan Stage

Load this prompt when an issue needs planning (no plan file exists or status is "not_planned").

## Planning Flow

### Check for Existing Plan

```bash
if [ -f ".tiki/plans/issue-${NUMBER}.json" ]; then
  cat ".tiki/plans/issue-${NUMBER}.json"
else
  echo "NO_PLAN"
fi
```

### If No Plan Exists

Display status and invoke planning:

```text
### Planning Issue #{number}

Issue #{number} has no plan. Invoking /tiki:plan-issue...
```

Invoke the plan-issue skill:

```text
Skill tool invocation:
- skill: "tiki:plan-issue"
- args: "{number}"
```

### After Planning

Verify plan was created:

```bash
cat ".tiki/plans/issue-${NUMBER}.json"
```

Display result:

```text
Plan created: {phaseCount} phases

| Phase | Title | Est. Context |
|-------|-------|--------------|
| {n} | {title} | {contextBudget}% |
```

### Planning Failure

If planning fails, present recovery options:

```text
### Planning Failed

Failed to create plan for issue #{number}.

### Recovery Options

1. **Retry planning** - Try /tiki:plan-issue again
2. **Skip issue** - Continue with remaining issues
3. **Pause YOLO** - Save state and exit for manual intervention

Enter choice:
```

Handle based on user choice:

**Retry**: Re-invoke plan-issue skill

**Skip**:
- Add issue to failedIssues with reason "planning_failed"
- Continue to next issue

**Pause**:
- Set yoloState.status to "paused"
- Set yoloState.pauseReason to "planning_failed"
- Save state and exit

## State Updates

After successful planning, update YOLO state:

```javascript
yoloState.currentIssue = issue.number;
yoloState.currentPhase = null;
```
