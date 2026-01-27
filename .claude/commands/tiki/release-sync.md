---
type: prompt
name: tiki:release-sync
description: Synchronize release state with GitHub milestone
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
argument-hint: <version> [--pull] [--two-way]
---

# Release Sync

Synchronize release state with GitHub milestone. Default: push Tiki to GitHub. Use `--pull` to pull from GitHub, or `--two-way` for bidirectional sync.

**Arguments:** `$ARGUMENTS`

- `<version>` (required): Version to sync
- `--pull`: Pull GitHub -> Tiki
- `--two-way`: Bidirectional merge

If both --pull and --two-way: error and show usage.

## Step 1: Load Release

```bash
VERSION="<parsed-version>"
RELEASE_FILE=".tiki/releases/${VERSION}.json"
```

If not found, check `.tiki/releases/archive/`. If still not found:

```text
Release "{version}" not found.
Available: {list releases}
Create: /tiki:release-new {version}
```

## Step 2: Check GitHub Milestone

```bash
REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"')
MILESTONE=$(gh api "repos/${REPO}/milestones" --jq ".[] | select(.title == \"${VERSION}\")")
```

**If milestone not found:**

- Default/two-way mode: Offer to create or skip
- Pull mode: Error - cannot pull without milestone

## Step 3: Fetch and Compare

Get milestone issues:

```bash
gh api "repos/${REPO}/issues?milestone=${MILESTONE_NUMBER}&state=all" \
  --jq '[.[] | {number, title, state}]'
```

Detect changes:

- `tikiOnly`: Issues in Tiki but not milestone
- `githubOnly`: Issues in milestone but not Tiki
- `statusMismatch`: Different completion states

## Step 4: Display Diff

**If no changes:**

```text
## Release {version} In Sync
No differences. State synchronized.
```

**If changes found:**

```text
## Sync Diff: {version}

### Tiki-only Issues
| Issue | Title | Status |

### GitHub-only Issues
| Issue | Title | State |

### Status Mismatches
| Issue | Tiki | GitHub |

Summary: {counts}
```

## Step 5: Apply Changes

**If no changes:** Done.

**If changes found:** Read `.tiki/prompts/release-sync/sync-operations.md` and follow instructions for the selected mode (default/pull/two-way).

**If two-way mode with status conflicts:** Also read `.tiki/prompts/release-sync/conflict-resolution.md` for conflict handling.

## Error Handling

- **gh unavailable:** Prompt to install/authenticate
- **API errors:** Show error, suggest retry
- **Write errors:** Report and exit without GitHub changes
