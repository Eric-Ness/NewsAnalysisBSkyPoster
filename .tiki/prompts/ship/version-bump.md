# Version Bump (Tiki Repo Only)

This step only applies when working on the Tiki project itself.

## Detection

Check if this is the Tiki repo by verifying `.claude/commands/tiki/ship.md` exists in the project root.

If the file does NOT exist, skip this step entirely.

## Process

### 1. Read version.json

Load `version.json` from the project root:

```json
{
  "version": "1.0.0",
  "releaseDate": "2026-01-14",
  "changelog": [...]
}
```

### 2. Increment Patch Version

Parse the current version string (e.g., "1.0.0") and increment the patch number:
- "1.0.0" -> "1.0.1"
- "2.3.9" -> "2.3.10"

### 3. Update Fields

- Set `version` to the new version string
- Set `releaseDate` to today's date (YYYY-MM-DD format)

### 4. Add Changelog Entry

Add a new entry to the changelog array:

```json
{
  "version": "1.0.1",
  "date": "2026-01-15",
  "changes": [
    "Issue #34: Add user authentication"
  ]
}
```

Use the issue number and title from the plan file.

### 5. Write Back

Write the updated `version.json` back to the file.

## Missing version.json

If `version.json` doesn't exist, create it:

```json
{
  "version": "0.0.1",
  "releaseDate": "<today>",
  "changelog": [
    {
      "version": "0.0.1",
      "date": "<today>",
      "changes": [
        "Issue #<N>: <title>"
      ]
    }
  ]
}
```

## Output

Report version change in summary:
- "Version: 1.0.0 -> 1.0.1"

For non-Tiki projects, this step is skipped silently.
