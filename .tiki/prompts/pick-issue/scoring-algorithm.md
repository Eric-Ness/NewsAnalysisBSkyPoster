# Scoring Algorithm for Pick Issue

## Dependency Pattern Detection

Scan each issue body for dependency patterns:

| Pattern | Meaning |
|---------|---------|
| `blocked by #N`, `depends on #N`, `requires #N` | This issue is blocked by issue N |
| `blocks #N`, `unblocks #N` | This issue enables/unblocks issue N |

Build a map of:
- `blockedBy[issueNum]` = list of issues blocking this one
- `enables[issueNum]` = list of issues this one unblocks

## Scoring Formula

Calculate a score for each issue:

| Factor | Points | Description |
|--------|--------|-------------|
| Preferred label | +3 | Has any label from `preferLabels` |
| "blocking" label | +2 | Has a label containing "blocking" |
| Enables others | +2 per issue | For each issue this unblocks |
| Age bonus | +0.5 per week | Max 2 points (caps at 4 weeks old) |
| Blocked | -5 | If blocked by any open issue |
| Deferred label | -3 | Has any label from `deferLabels` |

**Score calculation pseudocode:**
```
score = 0
if has_preferred_label: score += 3
if has_blocking_label: score += 2
score += (issues_this_enables * 2)
score += min(2, weeks_old * 0.5)
if is_blocked: score -= 5
if has_defer_label: score -= 3
```

## Sort and Categorize

Sort issues by score descending, then separate into:
- **Recommended**: Top 3 non-blocked, non-deferred issues
- **Deferred**: Issues with defer labels (sorted by score)
- **Blocked**: Issues blocked by other open issues
