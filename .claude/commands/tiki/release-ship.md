---
type: prompt
name: tiki:release-ship
description: Ship a release (close issues, create tag, archive)
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
argument-hint: <version>
---

# Release Ship

Ship and archive a completed release. Verifies issues, closes milestone, archives release, optionally creates git tag.

**Usage:** `/tiki:release-ship v1.1`

## State Files

**Active release:** `.tiki/releases/<version>.json`
- Fields: version, createdAt, status, requirementsEnabled, githubMilestone, issues[], requirements{}

**Archived release:** `.tiki/releases/archive/<version>.json`
- Same fields plus: shippedAt, shippedBy, gitTag, summary{}

## Instructions

### Step 1: Parse Arguments

Extract version from `$ARGUMENTS`. Normalize with 'v' prefix if missing.

If missing: Show usage and suggest `/tiki:release-status` to list releases.

### Step 2: Load Release

```bash
VERSION="${version}"
[[ ! "$VERSION" =~ ^v ]] && VERSION="v${VERSION}"

if [ -f ".tiki/releases/${VERSION}.json" ]; then
  cat ".tiki/releases/${VERSION}.json"
elif [ -f ".tiki/releases/archive/${VERSION}.json" ]; then
  echo "ALREADY_SHIPPED"
else
  echo "NOT_FOUND"
fi
```

- **Not found:** List available releases, suggest `/tiki:release-new`
- **Already shipped:** Show ship date and archive location

### Step 3: Pre-Ship Verification

For each issue, verify GitHub state:

```bash
gh issue view <number> --json state --jq '.state'
```

Display checklist table: | # | Title | Release Status | GitHub | Check |

### Step 4: Block if Issues Not Closed

If any issues are OPEN on GitHub:

```
Cannot ship - {count} issues not closed on GitHub.

Options:
1. Close issues first: gh issue close <number>
2. Remove open issues from release
3. Cancel
```

Use AskUserQuestion for confirmation if removing issues.

### Step 5: Requirements Check (if enabled)

If `release.requirementsEnabled`:
1. Load `.tiki/requirements.json`
2. Build verification: total, implemented, verified, unverified[]
3. Display table: | ID | Requirement | Status | Verified |

### Step 6: Interactive Verification

If unverified requirements exist:

```
Options:
1. Verify interactively - Review each requirement
2. Mark all verified - Trust implementation
3. Skip verification - Ship without verifying
4. Cancel
```

For interactive: prompt Yes/No/Skip/View for each requirement.

### Step 7: Close Milestone

**Condition:** If `release.githubMilestone` exists, load `.tiki/prompts/release-ship/milestone-sync.md` for workflow.

Core command: `gh api repos/:owner/:repo/milestones/{number} -X PATCH -f state="closed"`

### Step 8: Archive Release

1. Get current user: `git config user.name || whoami`
2. Build archived release with: status="shipped", shippedAt, shippedBy, gitTag, summary{}
3. Create archive: `mkdir -p .tiki/releases/archive`
4. Write to `.tiki/releases/archive/${VERSION}.json`
5. Remove `.tiki/releases/${VERSION}.json`
6. Update `.tiki/requirements.json` if modified

### Step 9: Git Tag (Optional)

Prompt user:
1. Create and push to remote
2. Create local only
3. Skip

```bash
git tag -a "${VERSION}" -m "Release ${VERSION}"
git push origin "${VERSION}"  # if pushing
```

### Step 10: Ship Summary

Display:
- Version, shipped at/by, duration
- Issues completed table
- Requirements summary (if enabled)
- Actions taken (archived, milestone, tag)
- Files updated
- What's next (other releases or create new)

## Error Handling

**Condition:** On any step failure, load `.tiki/prompts/release-ship/rollback-instructions.md` for recovery guidance.

Key errors: release not found, GitHub API errors, git tag errors, archive permission errors, corrupted files.

## Changelog Generation

**Condition:** If `--changelog` flag provided, load `.tiki/prompts/release-ship/changelog-generation.md` for workflow.
