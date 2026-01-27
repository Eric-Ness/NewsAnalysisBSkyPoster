---
type: prompt
name: tiki:cleanup
description: Remove temporary file artifacts created during Tiki execution (tmpclaude-*, nul, etc.)
allowed-tools: Bash, Glob
---

# Cleanup

Remove temporary file artifacts that may be left behind after Tiki execution.

## Usage

```text
/tiki:cleanup
/tiki:cleanup --dry-run    # Preview what would be deleted
```

## Instructions

### Step 1: Find Artifacts

Search for common temporary artifacts in the project root:

```bash
# List artifacts that would be cleaned up
ls -la ./tmpclaude-* ./nul ./NUL ./.tmp-* 2>/dev/null || echo "No artifacts in root"

# Check .tiki directory
ls -la .tiki/tmp-* .tiki/*.tmp 2>/dev/null || echo "No artifacts in .tiki"
```

### Step 2: Handle Dry Run

If `--dry-run` flag is provided, display what would be deleted and exit:

```text
## Cleanup Preview (dry-run)

Would delete:
- ./tmpclaude-3eb3-cwd
- ./nul
- .tiki/tmp-context.json

Run `/tiki:cleanup` to delete these files.
```

### Step 3: Delete Artifacts

Remove the temporary files:

```bash
# Remove common temporary artifacts from the project root
rm -f ./tmpclaude-* 2>/dev/null && echo "Removed tmpclaude-* files" || true
rm -f ./nul ./NUL 2>/dev/null && echo "Removed nul files" || true
rm -f ./.tmp-* 2>/dev/null && echo "Removed .tmp-* files" || true

# Clean up .tiki directory temp files
rm -f .tiki/tmp-* .tiki/*.tmp 2>/dev/null && echo "Removed .tiki temp files" || true
```

### Step 4: Report Results

```text
## Cleanup Complete

Removed:
- X tmpclaude-* files
- X nul/NUL files
- X .tiki temp files

Project root is clean.
```

If nothing was found:

```text
## Cleanup Complete

No temporary artifacts found. Project root is already clean.
```

## Known Artifacts

| Pattern | Source | Description |
|---------|--------|-------------|
| `tmpclaude-*` | Sub-agents | Temporary context/output files from Task tool |
| `nul` / `NUL` | Windows | Null device references that become actual files |
| `.tmp-*` | Various | General temporary files |
| `.tiki/tmp-*` | Tiki | Temporary state or context files |
| `.tiki/*.tmp` | Tiki | Temporary files in .tiki directory |

## Examples

### Example 1: Standard Cleanup

```text
User: /tiki:cleanup

Claude: ## Cleanup

Scanning for temporary artifacts...

Found:
- ./tmpclaude-3eb3-cwd
- ./tmpclaude-a1f2-output
- ./nul

Removing artifacts...

## Cleanup Complete

Removed:
- 2 tmpclaude-* files
- 1 nul file

Project root is clean.
```

### Example 2: Dry Run

```text
User: /tiki:cleanup --dry-run

Claude: ## Cleanup Preview (dry-run)

Would delete:
- ./tmpclaude-3eb3-cwd
- ./nul

Run `/tiki:cleanup` to delete these files.
```

### Example 3: Nothing to Clean

```text
User: /tiki:cleanup

Claude: ## Cleanup Complete

No temporary artifacts found. Project root is already clean.
```

## Notes

- This skill is safe to run at any time
- Files are deleted silently if they don't exist (no errors)
- The cleanup is idempotent - running multiple times has no additional effect
- Consider running after `/tiki:execute` or `/tiki:yolo` if you notice artifacts
