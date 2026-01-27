# Issue Selection Workflow

Select issues for the release from open GitHub issues.

## Group Issues by Theme

Analyze issue titles, bodies, and labels:

**Label-based grouping (priority):**
- bug, fix, defect -> "Bug Fixes"
- feature, enhancement -> "Features"
- docs, documentation -> "Documentation"
- security, auth -> "Security"
- performance, perf -> "Performance"
- tech-debt, refactor -> "Technical Debt"
- test -> "Testing"

**Title keyword fallback:**
- fix, bug, error, crash -> "Bug Fixes"
- add, implement, create, new -> "Features"
- update, improve, enhance -> "Enhancements"
- doc, readme -> "Documentation"
- refactor, cleanup -> "Technical Debt"
- Default -> "Other"

Display grouped table:
```text
### {Category} ({n} issues)
| # | Title | Labels |
|---|-------|--------|
```

## Selection Modes

Prompt user with AskUserQuestion:

**Option 1: By Category**
Select categories by number (comma-separated or "all").

**Option 2: Individually**
Enter issue numbers to include (comma-separated).
Validate each number exists in fetched issues.

**Option 3: Recommended**
Score issues:
- +3: priority label (high-priority, critical, urgent)
- +2: blocking label or enables other issues
- +1: Age > 2 weeks
- -3: defer label (backlog, someday)
- -5: Blocked by another open issue

Display top 10 recommendations with scores and reasons.

**Option 4: All Issues**
Confirm adding all open issues.

**Option 5: None**
Create empty release (add issues later).

## Validation

Invalid selections:
```text
The following issue numbers were not found: #99, #100
Valid issues: {list}
Please re-enter your selection:
```
