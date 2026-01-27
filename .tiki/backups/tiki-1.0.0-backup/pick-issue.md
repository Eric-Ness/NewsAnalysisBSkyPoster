---
type: prompt
name: tiki:pick-issue
description: Analyze open GitHub issues and recommend which one to work on next, with reasoning.
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: [--limit N]
---

# Pick Issue

Analyze open GitHub issues and recommend which one to work on next based on priority, dependencies, and age.

## Usage

```
/tiki:pick-issue
/tiki:pick-issue --limit 15
```

## Instructions

### Step 1: Parse Arguments and Config

Extract `--limit N` from arguments (default 25).

Read `.tiki/config.json` for `pickIssue` settings:

- `preferLabels`: Labels that boost priority (default: `["high-priority", "critical"]`)
- `deferLabels`: Labels that reduce priority (default: `["backlog", "someday"]`)
- `excludeLabels`: Labels that exclude issues (default: `["wontfix", "duplicate"]`)
- `maxIssues`: Maximum issues to fetch (default: 25)

### Step 2: Fetch Open Issues

```bash
gh issue list --state open --limit <N> --json number,title,labels,body,createdAt
```

Filter out issues with any `excludeLabels`.

### Step 3: Score and Rank

Read `.tiki/prompts/pick-issue/scoring-algorithm.md` for:

- Dependency pattern detection (blocked by, enables)
- Scoring formula with points breakdown
- Sort and categorize logic

### Step 4: Display Results

Read `.tiki/prompts/pick-issue/output-formats.md` for:

- Standard output format with recommendations
- Deferred and blocked sections
- Error handling (no issues, gh errors, no recommendations)

## Configuration

The `pickIssue` section in `.tiki/config.json` controls behavior:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `preferLabels` | string[] | `["high-priority", "critical"]` | Labels that boost priority (+3) |
| `deferLabels` | string[] | `["backlog", "someday"]` | Labels that reduce priority (-3) |
| `excludeLabels` | string[] | `["wontfix", "duplicate"]` | Labels that exclude issues entirely |
| `maxIssues` | number | 25 | Maximum issues to fetch and analyze |

## Notes

- This command is read-only - it never modifies state or issues
- Use `/tiki:whats-next` for Tiki state; use this for GitHub issue selection
- Combine with `/tiki:review-issue` to evaluate the top pick before planning
