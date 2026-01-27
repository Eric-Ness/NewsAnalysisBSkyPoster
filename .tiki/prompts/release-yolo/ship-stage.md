# Ship Stage

Load this prompt after all phases complete successfully.

## Ship Flow

### Display Status

```text
### Shipping Issue #{number}

All phases complete. Shipping issue...
```

### Invoke Ship

```text
Skill tool invocation:
- skill: "tiki:ship"
- args: "{number}"
```

The ship command handles:
1. Final verification
2. Git commit if needed
3. Closing GitHub issue
4. Updating release tracking

### Display Result

```text
Issue #{number} shipped.
{If requirements addressed:}Requirements marked as implemented: {requirementIds}

Release progress: {completedCount}/{totalCount} ({percent}%)
```

### Ship Failure

If ship fails, present options:

```text
### Ship Failed

Failed to ship issue #{number}.
Error: {errorMessage}

Options:
1. **Retry** - Attempt ship again
2. **Skip** - Mark issue as completed locally without closing GitHub issue
3. **Pause** - Save state for manual intervention

Enter choice:
```

## State Updates

After successful ship:

```javascript
yoloState.completedIssues.push(issue.number);
yoloState.currentIssue = null;
yoloState.currentPhase = null;
```

Update release file:

```javascript
release.issues.find(i => i.number === issue.number).status = 'completed';
release.issues.find(i => i.number === issue.number).completedAt = new Date().toISOString();
```

## Requirements Integration

If issue addresses requirements, display:

```text
Requirements addressed by this issue:
{For each requirement:}
- {req.id}: {req.text}
```
