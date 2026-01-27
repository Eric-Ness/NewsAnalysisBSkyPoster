---
type: prompt
name: tiki:release-remove
description: Remove an issue from its release
allowed-tools: Bash, Read, Write, Glob, Grep
argument-hint: <issue>
---

# Release Remove

Remove an issue from a release with optional handling of orphaned requirements.

**Usage:** `/tiki:release-remove <issue>`

Read `.tiki/prompts/release-remove/helper-functions.md` for helper function implementations (findReleaseForIssue, saveRelease, findOrphanedRequirements).

## Flow

### Step 1: Parse Arguments

Extract issue number from `$ARGUMENTS`. If missing, show usage and suggest `/tiki:release-status` to find issue's release.

### Step 2: Find Issue's Release

Search `.tiki/releases/*.json` for the issue. Use grep to find which release file contains `"number": {issueNumber}`. If not found, show error with suggestions to add via `/tiki:release-add`.

### Step 3: Display Issue Details

Show table with: Number, Title, Status, Release version, Requirements (if any), Phase progress (if planned).

### Step 4: Handle Orphaned Requirements

If issue has requirements, check for orphans using findOrphanedRequirements logic.

**If orphans exist:** Read `.tiki/prompts/release-remove/orphaned-requirements.md` for the interactive handling workflow (keep/clear/cancel options).

**If no orphans:** Proceed directly to confirmation.

### Step 5: Confirm Removal

Prompt: `Confirm removal of issue #{number} from release {version}? [y/N]`

If declined, exit with "Cancelled" message.

### Step 6: Update Release File

1. Remove issue from `release.issues` array
2. If `requirementsEnabled`, recalculate requirements totals and implemented counts
3. Write updated JSON to `.tiki/releases/{version}.json`

### Step 7: GitHub Milestone Sync

If release has `milestone.number`, remove milestone from issue:

```bash
gh issue edit {issueNumber} --milestone ""
```

### Step 8: Display Results

Show confirmation with:

- Issue removed message
- Updated progress bar and issue counts by status
- Requirements coverage before/after (if enabled)
- Uncovered requirements list (if orphans kept)
- Next steps: `/tiki:release-status {version}` or add new issues

## Error Handling

| Error                     | Response                                          |
|---------------------------|---------------------------------------------------|
| Issue not in any release  | Show error, suggest `/tiki:release-add`           |
| Release file corrupted    | Show recovery steps (check JSON, backup, recreate)|
| Permission error          | Show file permissions check command               |
