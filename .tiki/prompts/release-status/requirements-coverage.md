# Requirements Coverage Display

Show requirements implementation status for releases with requirements tracking enabled.

## Prerequisites

Only load this prompt when `release.requirementsEnabled` is true.

## Load Requirements

```bash
cat .tiki/requirements.json 2>/dev/null
```

## Build Coverage Matrix

For each requirement in requirements.json:
1. Initialize as 'not_covered'
2. Map issues to requirements via issue.requirements[]
3. Update status based on linked issue status:
   - Issue completed -> 'implemented'
   - Issue in_progress -> 'in_progress'
   - Issue planned -> 'planned'
   - No linked issue -> 'not_covered'

## Display Requirements Table

```text
### Requirements Coverage

| ID | Requirement | Status | Addressed By |
|----|-------------|--------|--------------|
| AUTH-01 | User login | ✓ implemented | #34 |
| AUTH-02 | Session management | ✓ implemented | #34 |
| AUTH-03 | Password reset | ◐ in_progress | #35 |
| UI-01 | Dark mode support | ○ planned | #36 |
| UI-02 | Responsive layout | · not_covered | - |

**Summary:**
- Total requirements: {total}
- Implemented: {implemented} ({implementedPercent}%)
- In Progress: {inProgress}
- Not Covered: {notCovered}
```

**Status Icons:**
- ✓ = implemented (completed issue addresses it)
- ◐ = in_progress (in-progress issue addresses it)
- ○ = planned (planned issue addresses it)
- · = not_covered (no issue addresses it)

## Coverage Warnings

If any requirements are not covered:

```text
### Coverage Gaps

The following requirements have no assigned issues:
{list of not_covered requirements}

Consider:
- Creating issues for uncovered requirements
- Adding requirement mappings to existing issues
```
