# Update Release Progress

Updates release and requirements tracking when the shipped issue is part of a release.

**CRITICAL: This step should NEVER cause ship to fail.** All errors are warnings only.

## Check If Issue Is In A Release

### From Plan File

Check if the plan has a `release` field:
```javascript
const planRelease = plan.release; // { version: "v1.1", milestone: "..." } or undefined
```

### From Release Files

If no release in plan, scan release files:
```bash
for file in .tiki/releases/*.json; do
  if grep -q "\"number\": $ISSUE_NUMBER" "$file" 2>/dev/null; then
    echo "$file"
    break
  fi
done
```

If issue is not in any release, skip this step silently.

## Update Issue Status In Release File

1. Load `.tiki/releases/<version>.json`
2. Find the issue in the `issues` array
3. Update the issue entry:

```javascript
issueEntry.status = 'completed';
issueEntry.completedAt = new Date().toISOString();
issueEntry.currentPhase = null;
```

4. Write the updated release file

### Error Handling

- Release file not found: Log warning, continue
- Invalid JSON: Log warning, continue
- Issue not found in release: Continue silently

## Update Requirements Status

If the issue addresses requirements (from `plan.addressesRequirements` or release issue's `requirements` field):

1. Load `.tiki/requirements.json`
2. For each requirement ID:
   - Find requirement in categories
   - If status is 'pending', set to 'implemented'
   - Add issue number to `implementedBy` array (if not present)
   - Update `updatedAt` timestamp
3. Write updated requirements.json

### Error Handling

- requirements.json not found: Skip silently
- Invalid JSON: Log warning, continue
- Requirement not found: Continue silently

## Track Updates For Summary

Store for Step 8 summary output:

| Field | Type | Description |
|-------|------|-------------|
| `releaseUpdated` | boolean | Whether release was updated |
| `releaseVersion` | string | The release version |
| `releaseProgress` | object | `{ completed: number, total: number }` |
| `remainingIssues` | array | `[{ number, title }]` for incomplete issues |
| `requirementsUpdated` | array | Requirement IDs that were updated |

## Summary Output Format

If `releaseUpdated` is true, append to ship summary:

```
Release Progress:
- Requirement AUTH-01 marked as "implemented"
- Release v1.1 progress: 3/5 issues (60%)

Remaining issues in v1.1:
  #37: Add password reset
  #38: Add session management

When all issues complete, run: /tiki:release-ship v1.1
```

When all issues complete:
```
All issues in v1.1 complete!
Ready to ship release: /tiki:release-ship v1.1
```

If update failed with warnings:
```
Note: Could not update release tracking (see warnings above).
The issue was shipped successfully.
```
