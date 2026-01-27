# Table Format

Generate a table-based roadmap view for compact project status scanning.

## Output Structure

```markdown
## Project Roadmap

| Release | Status | Issues | Progress | Requirements |
|---------|--------|--------|----------|--------------|
| v1.0 | shipped | 3 | 100% | 3/3 |
| v1.1 | active | 5 | 40% | 2/4 |
| v2.0 | planned | 3 | 0% | 0/2 |

### Issue Details

#### v1.1 (active - 40% complete)
| # | Title | Status | Requirements |
|---|-------|--------|--------------|
| 20 | Feature A | ◐ in_progress | MULTI-01 |
| 21 | Feature B | ○ planned | MULTI-02, MULTI-03 |
| 22 | Feature C | · not_planned | - |
```

## Release Summary Table

First table shows overview of all releases:
- **Release**: Version string
- **Status**: shipped/active/planned
- **Issues**: Count of issues in release
- **Progress**: Percentage of completed issues
- **Requirements**: `implemented/total` or `-` if none

## Issue Details Table

For each non-shipped release, show detailed issue table:
- **#**: Issue number
- **Title**: Truncated to 40 characters
- **Status**: Symbol + status name
- **Requirements**: Comma-separated requirement IDs or `-`

## Status Symbols

```
✓  completed
◐  in_progress
○  planned
·  not_planned
```

## Requirements Coverage Calculation

Count unique requirements across all issues in release:
- Total: all requirements linked to any issue
- Implemented: requirements where linked issue is completed
- Display as `implemented/total` or `-` if no requirements

## Generation Steps

1. Sort releases by version
2. Generate release summary table header
3. For each release, add summary row
4. Add "### Issue Details" section
5. For each non-shipped release:
   - Add release header with progress
   - Generate issue details table
   - Skip shipped releases (they're historical)
