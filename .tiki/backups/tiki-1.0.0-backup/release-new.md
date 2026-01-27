---
type: prompt
name: tiki:release-new
description: Create a new release version with interactive issue selection
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
argument-hint: <version> [--sync-github]
---

# Release New

Create a new release version with interactive issue selection.

## Usage

```text
/tiki:release-new v1.1
/tiki:release-new v1.1 --sync-github
```

- `<version>` (required): Version identifier (e.g., v1.1, 2.0.0-beta)
- `--sync-github`: Create and sync GitHub milestone

## Step 1: Parse and Validate

Parse: `$ARGUMENTS` -> extract version and syncGithub flag.

Validate version format: `^v?\d+\.\d+(\.\d+)?(-[a-zA-Z0-9.]+)?$`

Valid: v1.0.0, v1.1, 2.0.0-beta, v1.0.0-rc.1

If invalid, show error with usage examples and exit.

## Step 2: Check Existing Release

```bash
VERSION="v1.1"  # normalized
if [ -f ".tiki/releases/${VERSION}.json" ]; then echo "EXISTS"; fi
```

If exists, prompt via AskUserQuestion:
1. View existing - run `/tiki:release-status {version}`
2. Overwrite - backup and continue
3. Cancel - exit

## Step 3: Check Requirements

```bash
[ -f ".tiki/requirements.json" ] && echo "FOUND"
```

If not found, prompt:
1. Continue without requirements
2. Define requirements first (`/tiki:define-requirements`)
3. Cancel

If found, set `requirementsEnabled: true` and load for later mapping.

## Step 4: Fetch Open Issues

```bash
gh issue list --state open --json number,title,body,labels --limit 100
```

If gh fails or no issues found, prompt:
1. Create empty release
2. Cancel

## Step 5: Issue Selection

**CONDITIONAL LOAD**: Read `.tiki/prompts/release-new/issue-selection.md`

Group issues by theme (labels > title keywords), display grouped tables, then prompt for selection mode (by category, individually, recommended, all, or none).

## Step 6: Requirements Mapping

**CONDITIONAL LOAD** (if requirementsEnabled): Read `.tiki/prompts/release-new/requirements-mapping.md`

For each selected issue, suggest requirements based on keywords, allow editing, support batch mode for many issues.

## Step 7: Create Release File

```bash
mkdir -p .tiki/releases
```

Write to `.tiki/releases/<version>.json`:

```json
{
  "version": "v1.1",
  "createdAt": "{ISO timestamp}",
  "status": "active",
  "requirementsEnabled": true,
  "githubMilestone": null,
  "issues": [
    {
      "number": 42,
      "title": "Issue title",
      "status": "not_planned",
      "requirements": ["REQ-01"],
      "currentPhase": null,
      "totalPhases": null,
      "completedAt": null
    }
  ],
  "requirements": { "total": 0, "implemented": 0, "verified": 0 }
}
```

## Step 8: GitHub Milestone Sync

**CONDITIONAL LOAD** (if --sync-github): Read `.tiki/prompts/release-new/milestone-creation.md`

Check for existing milestone, create if needed, assign issues, update release file with milestone info.

## Step 9: Display Summary

```text
## Release Created

### Release: {version}
| Field | Value |
|-------|-------|
| Version | {version} |
| Status | active |
| Issues | {count} |
| Requirements | {yes/no} |
| Milestone | {url or None} |

### Issues Included
| # | Title | Requirements |
|---|-------|--------------|

### Next Steps
- `/tiki:get-issue {number}` to start working
- `/tiki:release-status` to view progress
- `/tiki:release-add {number}` to add more issues
- `/tiki:release-ship {version}` when ready
```

If multiple active releases exist, note them in output.
