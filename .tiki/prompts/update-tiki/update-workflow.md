# Update Workflow

Steps for performing the actual Tiki update after version comparison.

## Step 5: Create Backup

Create a backup directory:
```
.tiki/backups/commands-<YYYYMMDD-HHMMSS>/
```

Copy all files from `.claude/commands/tiki/` to the backup directory.

Report: "Backed up current commands to .tiki/backups/commands-<timestamp>/"

## Step 6: Clone Repository

Clone the Tiki repository to a temporary directory:

```bash
git clone --depth 1 https://github.com/Eric-Ness/Tiki.git <temp-dir>
```

Use a temporary directory name like `tmpclaude-tiki-update-<random>`.

## Step 7: Copy Updated Files

Copy all files from `<temp-dir>/.claude/commands/tiki/` to `.claude/commands/tiki/`.

For each file copied, report:
- `(new)` if the file didn't exist before
- `(updated)` if the file existed and was replaced
- `(unchanged)` if the file content is identical

## Step 8: Update Local Version File

Update `.claude/commands/tiki/version.json` with:
- New version number from remote
- Current date as `installedDate`
- Keep the `source` URL

## Step 9: Cleanup

Remove the temporary clone directory:

```bash
rm -rf <temp-dir>
```

## Step 10: Report Results

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
