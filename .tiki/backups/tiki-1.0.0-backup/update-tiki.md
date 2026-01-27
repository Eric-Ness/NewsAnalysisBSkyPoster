# Update Tiki

Update your Tiki installation to the latest version from GitHub.

## Arguments

- `--dry-run` - Show what would be updated without making changes

## Instructions

### Step 1: Read Local Version

Read the local version file at `.claude/commands/tiki/version.json`.

If the file doesn't exist, assume version is "0.0.0" (unknown/legacy installation).

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

### Step 5: Perform Update

Read `.tiki/prompts/update-tiki/update-workflow.md` for backup, clone, copy, and cleanup steps.

### Step 6: Handle Errors

If errors occur, read `.tiki/prompts/update-tiki/error-handling.md` for guidance.

### Step 7: Report Results

Show summary: version change, files updated/new/unchanged, backup location.

For example output formats, see `.tiki/prompts/update-tiki/example-outputs.md`.
