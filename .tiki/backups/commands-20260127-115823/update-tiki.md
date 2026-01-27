# Update Tiki

Update your Tiki installation to the latest version from GitHub.

## Arguments

- `--dry-run` - Show what would be updated without making changes

## Instructions

### Step 1: Read Local Version

Read the local version file at `.claude/commands/tiki/version.json`.

If the file doesn't exist, assume version is "0.0.0" (unknown/legacy installation).

Store the local version for comparison.

### Step 2: Fetch Remote Version

Fetch the remote version file from GitHub:

```
https://raw.githubusercontent.com/Eric-Ness/Tiki/main/version.json
```

Use WebFetch to retrieve this file. Parse the JSON to get:
- `version` - The latest version number
- `changelog` - Array of version changes

### Step 3: Compare Versions

Compare local version against remote version.

If versions are the same:
- Report "Tiki is already up to date (version X.X.X)"
- Exit

If remote is newer:
- Display the version difference
- Show changelog entries for versions newer than the local version
- Continue to Step 4

### Step 4: Handle Dry Run

If `--dry-run` flag is present:
- Report what would be updated
- List all command files that would be replaced
- Exit without making changes

### Step 5: Create Backup

Create a backup directory:
```
.tiki/backups/commands-<YYYYMMDD-HHMMSS>/
```

Copy all files from `.claude/commands/tiki/` to the backup directory.

Report: "Backed up current commands to .tiki/backups/commands-<timestamp>/"

### Step 6: Clone Repository

Clone the Tiki repository to a temporary directory:

```bash
git clone --depth 1 https://github.com/Eric-Ness/Tiki.git <temp-dir>
```

Use a temporary directory name like `tmpclaude-tiki-update-<random>`.

### Step 7: Copy Updated Files

Copy all files from `<temp-dir>/.claude/commands/tiki/` to `.claude/commands/tiki/`.

For each file copied, report:
- `(new)` if the file didn't exist before
- `(updated)` if the file existed and was replaced
- `(unchanged)` if the file content is identical

### Step 8: Update Local Version File

Update `.claude/commands/tiki/version.json` with:
- New version number from remote
- Current date as `installedDate`
- Keep the `source` URL

### Step 9: Cleanup

Remove the temporary clone directory:

```bash
rm -rf <temp-dir>
```

### Step 10: Report Results

Display a summary:

```
## Tiki Update Complete

Updated from version X.X.X to Y.Y.Y

Files updated:
- execute.md (updated)
- heal.md (new)
- plan-issue.md (updated)
...

Backup saved to: .tiki/backups/commands-<timestamp>/

To rollback, copy files from the backup directory back to .claude/commands/tiki/
```

---

## Error Handling

### Network Errors
If unable to fetch remote version or clone repository:
- Report the error clearly
- Suggest checking internet connection
- Do not modify any local files

### Git Not Available
If `git clone` fails:
- Report that git is required
- Suggest installing git or using GitHub CLI

### Backup Failure
If unable to create backup:
- Stop the update process
- Report the error
- Do not proceed without backup

### Partial Update Failure
If copying files fails mid-process:
- Report which files were updated
- Point user to backup for recovery
- Suggest manual completion or retry

---

## Example Outputs

### Already Up to Date

```
## Tiki Update Check

Local version:  1.2.0
Remote version: 1.2.0

Tiki is already up to date!
```

### Update Available

```
## Tiki Update Check

Local version:  1.0.0
Remote version: 1.2.0

### What's New

**Version 1.2.0** (2026-01-20)
- Added /tiki:heal command for auto-fixing failed phases
- Improved phase dependency validation
- Fixed issue with pause/resume state

**Version 1.1.0** (2026-01-17)
- Added TDD support with test-creator
- New assess-code command for codebase health checks

### Updating...

Backing up to .tiki/backups/commands-20260121-143022/

Cloning latest Tiki...

Copying files:
  add-issue.md (unchanged)
  adr.md (unchanged)
  assess-code.md (updated)
  audit-plan.md (unchanged)
  commit.md (unchanged)
  create-issues.md (unchanged)
  discuss-phases.md (unchanged)
  execute.md (updated)
  get-issue.md (unchanged)
  heal.md (new)
  map-codebase.md (unchanged)
  pause.md (unchanged)
  plan-issue.md (updated)
  redo-phase.md (unchanged)
  resume.md (unchanged)
  review-queue.md (unchanged)
  skip-phase.md (unchanged)
  state.md (unchanged)
  test-creator.md (updated)
  update-claude.md (unchanged)
  update-tiki.md (updated)
  version.json (updated)
  whats-next.md (unchanged)

Cleaning up...

## Update Complete!

Tiki updated from 1.0.0 to 1.2.0

3 files updated, 1 new file, 19 unchanged

Backup saved to: .tiki/backups/commands-20260121-143022/
```

### Dry Run

```
## Tiki Update Check (Dry Run)

Local version:  1.0.0
Remote version: 1.2.0

Would update the following files:
- assess-code.md
- execute.md
- heal.md (new)
- plan-issue.md
- test-creator.md
- update-tiki.md
- version.json

Run without --dry-run to apply updates.
```
