# Failure Handling and Results

Track verification results and provide recommendations.

## Result Object Structure

```javascript
const results = {
  issue: { number, title, url },
  verifiedAt: new Date().toISOString(),
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0,
    pending: 0,
    passRate: 0
  },
  phases: []  // Grouped items by phase
};
```

## Recording Results

For each item:
- `status`: pass, fail, skip, or pending
- `verifiedAt`: ISO timestamp
- `notes`: User-provided notes (failures, skip reasons)

Calculate pass rate: `Math.round((passed / total) * 100)`

## Summary Display

```
## Verification Summary for Issue #N

| Status  | Count |
|---------|-------|
| Passed  | X     |
| Failed  | Y     |
| Skipped | Z     |
| Pending | W     |

Pass Rate: N% (passed/total)
```

## Failure Sections

**Failed Items:**
```
### Failed Items

**Phase N, Item M:** {description}
- Status: FAIL
- Notes: "{user notes}"
```

**Skipped Items:**
```
### Skipped Items

**Phase N, Item M:** {description}
- Status: SKIPPED
- Reason: "{reason if provided}"
```

**Pending Clarification:**
```
### Pending Clarification

**Phase N, Item M:** {description}
- Status: PENDING
- Question: "{clarification question}"
```

## Recommendations

Based on pass rate:
- **100%:** "All verifications passed. Ready to ship!"
- **80-99%:** "Most verifications passed. Review failed items before shipping."
- **50-79%:** "Significant failures detected. Address issues before proceeding."
- **<50%:** "Critical issues found. Do not ship until resolved."

Add note if pending items exist: "Note: {N} item(s) require clarification before full verification."

## UAT Report (--report flag)

Write to `.tiki/reports/uat-issue-<number>.json`:
```json
{
  "issue": { "number": N, "title": "...", "url": "..." },
  "verifiedAt": "ISO timestamp",
  "verifiedBy": "user",
  "summary": { "total": N, "passed": N, "failed": N, "skipped": N, "passRate": N },
  "phases": [...],
  "recommendation": "..."
}
```
