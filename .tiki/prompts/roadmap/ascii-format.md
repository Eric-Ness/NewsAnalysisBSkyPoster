# ASCII Timeline Format

Generate an ASCII timeline visualization of the project roadmap.

## Output Structure

```
## Project Roadmap

### Timeline

v1.0 (shipped 2026-01-10)
├── #12: Core execution framework ✓
├── #14: Auto-fix infrastructure ✓
└── #15: Trigger processing ✓

v1.1 (active - 40% complete)
├── #20: Feature A ◐
├── #21: Feature B ○
└── #22: Feature C ·

v2.0 (planned)
├── #30: Future feature ·
└── #31: Another feature ·

Legend: ✓ completed | ◐ in_progress | ○ planned | · not_planned

### Summary

| Status | Count |
|--------|-------|
| Completed | 3 |
| In Progress | 1 |
| Planned | 2 |
| Not Planned | 1 |
| **Total** | **7** |

Progress: 3/7 issues complete (43%)
```

## Release Status Line

| Condition | Format | Example |
|-----------|--------|---------|
| shipped | `{version} (shipped {date})` | `v1.0 (shipped 2026-01-10)` |
| active | `{version} (active - {progress}% complete)` | `v1.1 (active - 40%)` |
| planned | `{version} (planned)` | `v2.0 (planned)` |

## Issue Tree Formatting

- Use `├──` for all issues except the last
- Use `└──` for the last issue in each release
- Format: `{tree_char} #{number}: {title} {status_symbol}`
- Truncate titles longer than 50 characters with "..."

## Status Symbols

```
✓  completed
◐  in_progress
○  planned
·  not_planned
```

## Summary Generation

Count all issues across releases by status. Calculate overall progress as `completed / total * 100`.

## Generation Steps

1. Sort releases by version (semver order)
2. For each release:
   - Output release status line
   - Output each issue with tree character and status symbol
   - Add blank line after each release
3. Output legend line
4. Generate summary table with status counts
5. Output progress line
