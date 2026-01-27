---
type: prompt
name: tiki:release-add
description: Add one or more issues to a release with optional requirements mapping. Supports batch adding and --to flag for specific versions.
allowed-tools: Bash, Read, Write, Glob, Grep, Task
argument-hint: <issue> [<issue>...] [--to <version>]
---

# Release Add

Add GitHub issues to a release.

## Usage

```text
/tiki:release-add 34                    # Add single issue to active release
/tiki:release-add 34 --to v1.2          # Add to specific release
/tiki:release-add 23 24 25              # Add multiple issues
/tiki:release-add 23 24 25 --to v1.2    # Multiple to specific release
```

## Step 1: Parse Arguments

```text
Arguments: $ARGUMENTS

Extract:
- issueNumbers: Array of issue numbers
- targetVersion: Optional version from --to flag
```

If no issue numbers: show usage and exit.

## Step 2: Determine Target Release

**With --to flag:** Load `.tiki/releases/{version}.json` (normalize v prefix).

**Without --to:** Find most recent active release via `ls -t .tiki/releases/*.json`.

If release not found or no active releases: show error with available releases.

## Step 3: Validate Issues

For each issue number:

```bash
gh issue view <number> --json number,title,state,labels,body
```

**Validation checks:**

1. Issue exists on GitHub
2. Issue is not closed
3. Issue is not already in target release
4. Issue is not in another release (warn and prompt: Move/Skip/Cancel)

Report validation errors in table format. Proceed with valid issues only.

## Step 4: Add Issues

**Single Issue:** Show issue details table, check for existing plan, then add.

**Multiple Issues:** Load `.tiki/prompts/release-add/batch-mode.md` and follow batch workflow.

## Step 5: Requirements Mapping (Conditional)

If `release.requirementsEnabled` and `.tiki/requirements.json` exists:

- Load `.tiki/prompts/release-add/requirements-linking.md`
- Follow requirements mapping workflow

## Step 6: Update Release File

Build issue entry:

```javascript
{
  number, title,
  status: derived from plan (not_planned|planned|in_progress|completed),
  requirements: [],
  currentPhase, totalPhases, completedAt
}
```

Add to `release.issues[]`, update requirements totals, save file.

## Step 7: Milestone Sync (Conditional)

If `release.githubMilestone` exists:

- Load `.tiki/prompts/release-add/milestone-sync.md`
- Assign issues to milestone

## Step 8: Display Summary

```text
## Issues Added

Successfully added {count} issue(s) to release {version}.

| # | Title | Status | Requirements |
|---|-------|--------|--------------|

### Release Progress

{progressBar} {percent}%
{completed}/{total} issues complete
```

## Error Handling

- **Issue not found:** Report error, skip issue
- **Issue closed:** Prompt to add anyway (status: completed)
- **Already in release:** Report, no action needed
- **No active releases:** Prompt to create with `/tiki:release-new`
