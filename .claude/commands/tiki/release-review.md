---
type: prompt
name: tiki:release-review
description: Deep review all issues in a release before planning. Runs review-issue, deep-dives on warnings, and posts decisions as GitHub comments.
allowed-tools: [Read, Glob, Grep, Bash, Task, Write, Edit]
argument-hint: "[version] [--quiet] [--no-comment] [--issue N]"
---

# Release Review

Automated deep review workflow for all issues in a release before planning/execution.

## Usage

```text
/tiki:release-review v1.5              # Review all issues in v1.5
/tiki:release-review                   # Review active release
/tiki:release-review v1.5 --quiet      # Suppress output for clean issues
/tiki:release-review v1.5 --no-comment # Skip posting GitHub comments
/tiki:release-review v1.5 --issue 56   # Review only issue #56 in release
```

## Instructions

### Step 1: Parse Arguments

Parse from `$ARGUMENTS`:
- `version`: Release version (e.g., `v1.5`). Optional.
- `--quiet`: Suppress output for clean issues
- `--no-comment`: Skip posting GitHub comments
- `--issue N`: Review only specific issue number(s)

### Step 2: Load Release

If version specified:

```bash
cat .tiki/releases/{version}.json
```

If no version, find active release:

```bash
ls .tiki/releases/*.json
```

Look for release with `"status": "active"`. If none found, show error and exit.

Parse release JSON to get `issues` array with `number` and `title` for each.

### Step 3: Filter Issues

If `--issue` flag provided, filter to only those issue numbers.

Display pre-review summary:

```text
## Release Review: {version}

Reviewing {N} issues:
- #{number}: {title}
- #{number}: {title}
...
```

### Step 4: Review Loop

For each issue in the list:

#### 4a: Display Progress

```text
### Reviewing #{number}: {title}
```

#### 4b: Run Review

Use Task tool to spawn sub-agent:

```
Prompt: Run /tiki:review-issue {number} --yolo

Return the full output including the REVIEW_RESULT JSON block.
```

#### 4c: Parse Result

Extract the REVIEW_RESULT JSON from the output:

```
<!-- REVIEW_RESULT
{...json...}
REVIEW_RESULT -->
```

Parse to get:
- `verdict`: "blocked" | "warnings" | "clean"
- `blocking`: Array of blocking concerns
- `warnings`: Array of warning concerns

#### 4d: Handle by Verdict

**If verdict is "clean":**

Display (unless `--quiet`):

```text
#{number}: CLEAN - No concerns found
```

Continue to next issue.

**If verdict is "warnings" or "blocked":**

Display:

```text
#{number}: {VERDICT} - {count} concern(s) found
```

Proceed to deep-dive (Step 5).

### Step 5: Deep Dive (Conditional)

**Only execute if:** Verdict is "warnings" or "blocked"

Read the deep-dive prompt:

```bash
cat .tiki/prompts/release-review/deep-dive.md
```

Use Task tool to spawn a sub-agent with the deep-dive instructions, passing:
- Issue number and title
- List of warnings/blocking concerns from review
- The deep-dive prompt content

The sub-agent should:
1. Fetch the full issue details via `gh issue view`
2. Explore relevant code paths mentioned in the issue
3. Analyze each warning/blocker
4. Propose solutions or mitigations
5. Return structured findings

Capture the deep-dive output.

### Step 6: Post GitHub Comment (Conditional)

**Skip if:** `--no-comment` flag is set

Read the comment template:

```bash
cat .tiki/prompts/release-review/github-comment.md
```

Format the comment with:
- Warnings/blockers addressed
- Proposed approach for each
- Code references where relevant
- Rationale for decisions

Post comment:

```bash
gh issue comment {number} --body "{formatted_comment}"
```

Display:

```text
Posted analysis comment to #{number}
```

### Step 7: Track Results

Accumulate results for summary:

```json
{
  "reviewed": 5,
  "clean": 2,
  "warnings": 2,
  "blocked": 1,
  "commentsPosted": 3
}
```

### Step 8: Display Summary

Read summary template:

```bash
cat .tiki/prompts/release-review/summary-table.md
```

Display final summary table:

```text
## Release Review Complete: {version}

| Issue | Title | Verdict | Comment |
|-------|-------|---------|---------|
| #56 | Feature X | CLEAN | - |
| #57 | Bug fix Y | WARNINGS | Posted |
| #58 | Refactor Z | BLOCKED | Posted |

**Summary:** 5 reviewed | 2 clean | 2 warnings | 1 blocked | 3 comments posted

### Next Steps
- Address blocked issues before planning
- Review posted comments for warnings
- Ready: `/tiki:release-yolo {version}` when concerns addressed
```

## Error Handling

- **Release not found:** Show available releases and exit
- **Issue not in release:** Warn and skip
- **gh CLI error:** Report and continue to next issue
- **No issues to review:** Report "No issues in release" and exit
