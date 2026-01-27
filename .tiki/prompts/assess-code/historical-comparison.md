# Historical Comparison

Track score changes over time to measure improvement.

## Score History Table

Append new assessments to the history table in the report:

```markdown
## Score History

| Date | Score | Change | Notes |
|------|-------|--------|-------|
| {date} | {score} | {change} | {notes} |
```

## Calculating Change

1. Read previous assessment from `docs/CODE_QUALITY_ASSESSMENT.md`
2. Extract the most recent overall score
3. Calculate delta: `newScore - previousScore`
4. Format change: `+5`, `-3`, or `--` for initial

## Trend Display

Show trend in summary output:

```
**Overall Score: 72/100** (+5 from last assessment)
```

If score decreased, highlight areas of regression:
```
**Overall Score: 68/100** (-4 from last assessment)
Regression in: Security (-8), Testability (-3)
```

## Notes Field

Auto-generate notes based on largest score changes:
- If security improved: "Fixed security issues"
- If testability improved: "Added tests"
- If architecture improved: "Refactored structure"
- Otherwise: summarize the primary change
