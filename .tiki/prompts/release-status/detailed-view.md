# Detailed Single Release View

Display comprehensive status for a specific release version.

## Step S3: Update Issue Status from External Sources

For each issue in the release, refresh status from:

1. **GitHub Issue State:**
   ```bash
   gh issue view <number> --json state --jq '.state'
   ```

2. **Tiki Plan File:**
   ```bash
   cat .tiki/plans/issue-<number>.json 2>/dev/null
   ```

3. **Tiki State File:**
   ```bash
   cat .tiki/state/current.json 2>/dev/null
   ```

**Status Resolution Logic:**
- If GitHub state is CLOSED: status = 'completed'
- If current state has activeIssue matching: status = 'in_progress'
- If plan exists with all phases complete: status = 'completed'
- If plan exists with some phases complete: status = 'in_progress'
- If plan exists with no phases complete: status = 'planned'
- Otherwise: status = 'not_planned'

## Step S7: Display Progress Overview

```text
### Progress

{progressBar} {progress}%

{completed}/{total} issues complete

| Status | Count | Visual |
|--------|-------|--------|
| Completed | {completed} | {'●'.repeat(completed)} |
| In Progress | {inProgress} | {'◐'.repeat(inProgress)} |
| Planned | {planned} | {'○'.repeat(planned)} |
| Not Planned | {notPlanned} | {'·'.repeat(notPlanned)} |
```

## Step S8: Display Issues Table

```text
### Issues

| # | Title | Status | Phase | Progress |
|---|-------|--------|-------|----------|
| 34 | Add user authentication | ✓ completed | 3/3 | ██████████ |
| 35 | Fix login redirect | ◐ in_progress | 2/3 | ██████░░░░ |
| 36 | Implement dark mode | ○ planned | 0/4 | ░░░░░░░░░░ |
| 37 | Update API docs | · not_planned | - | - |
```

**Status Icons:** ✓ = completed, ◐ = in_progress, ○ = planned, · = not_planned

## Step S10: Display Timeline Visualization

```text
### Timeline

Issue Progress:
#34 ████████████████████████████████████████ ✓
#35 ████████████████████████░░░░░░░░░░░░░░░░ 60%
#36 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
#37 ---------------------------------------- not planned
```

## Step S11: Suggest Next Action

Based on release state, suggest appropriate action:

- **All complete:** `/tiki:release-ship {version}`
- **In-progress exists:** `/tiki:get-issue {number}` to continue
- **Planned exists:** `/tiki:execute` to start
- **Unplanned exists:** `/tiki:plan-issue` to plan
- **Empty release:** `/tiki:release-add <issue> --to {version}`
