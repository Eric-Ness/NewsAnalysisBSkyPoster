---
type: prompt
name: tiki:changelog
description: Show recent Tiki updates and changelog
allowed-tools: Read, Write, Bash
argument-hint: [version] [--all] [--since <version>] [--generate-file]
---

# Changelog

Display recent Tiki updates and version history.

## Usage

```
/tiki:changelog              # Show last 3 versions (default)
/tiki:changelog --all        # Show complete changelog
/tiki:changelog 1.0.10       # Show specific version
/tiki:changelog --since 1.0.5  # Show all versions since v1.0.5
/tiki:changelog --generate-file  # Generate/update CHANGELOG.md file
```

## Instructions

### Step 1: Read version.json

Read `version.json` from the repository root to get the changelog data:

```json
{
  "version": "1.0.14",
  "releaseDate": "2026-01-18",
  "changelog": [
    {
      "version": "1.0.14",
      "date": "2026-01-18",
      "changes": [
        "Issue #43: Add /tiki:roadmap for multi-release project visualization"
      ]
    }
  ]
}
```

### Step 2: Parse Arguments

Determine which entries to show based on the argument:

- **No argument**: Show the last 3 versions (default)
- **`--all`**: Show all changelog entries
- **`<version>`** (e.g., `1.0.10`): Show only that specific version
- **`--since <version>`** (e.g., `--since 1.0.5`): Show all versions from the specified version to current
- **`--generate-file`**: Generate or update CHANGELOG.md at the repository root

### Step 3: Display Changelog

Format the output in markdown with version headers and bullet points:

```markdown
## Tiki Changelog

### v1.0.14 (2026-01-18)
- Issue #43: Add /tiki:roadmap for multi-release project visualization

### v1.0.13 (2026-01-18)
- Issue #42: Add release automation and command integration

### v1.0.12 (2026-01-18)
- Issue #41: Add core release management system (/tiki:release)
```

For versions with multiple changes, list each as a separate bullet:

```markdown
### v1.0.0 (2026-01-14)
- Initial release
- Core workflow commands: get-issue, plan-issue, execute
- Execution control: pause, resume, skip-phase, redo-phase, heal
- Planning tools: audit-plan, discuss-phases
```

### Step 4: Generate CHANGELOG.md (optional)

When the `--generate-file` flag is present, generate or update a `CHANGELOG.md` file at the repository root.

**CHANGELOG.md format:**

```markdown
# Changelog

All notable changes to Tiki are documented in this file.

## [1.0.14] - 2026-01-18

### Added
- Issue #43: Add /tiki:roadmap for multi-release project visualization

## [1.0.13] - 2026-01-18

### Added
- Issue #42: Add release automation and command integration

## [1.0.0] - 2026-01-14

### Added
- Initial release
- Core workflow commands: get-issue, plan-issue, execute
- Execution control: pause, resume, skip-phase, redo-phase, heal
- Planning tools: audit-plan, discuss-phases
```

**Generation rules:**

1. Include ALL versions from version.json (not just the filtered subset)
2. Use `## [version] - date` format for version headers
3. Group changes under `### Added` section (all changes are additions)
4. If CHANGELOG.md already exists, overwrite it completely from version.json
5. After generating, display confirmation: "Generated CHANGELOG.md with {N} versions."

### Step 5: Handle Edge Cases

**Version not found:**
```
Version 1.0.99 not found in changelog.

Available versions: 1.0.14, 1.0.13, 1.0.12, ...
```

**--since version not found:**
```
Version 1.0.99 not found. Cannot show changes since that version.

Available versions: 1.0.14, 1.0.13, 1.0.12, ...
```

**Empty changelog:**
```
No changelog entries found.
```

## Output Format

Always output in this structure:

```markdown
## Tiki Changelog

{For each version to display:}
### v{version} ({date})
{For each change:}
- {change description}

{blank line between versions}
```

When showing a subset (default or --since), add a footer:

```markdown
---
Showing {N} of {total} versions. Use `--all` to see complete history.
```

## Notes

- Versions are displayed newest first (descending order)
- The changelog is read from `version.json` in the repository root
- Use `--generate-file` after releases to keep CHANGELOG.md in sync with version.json
- Without `--generate-file`, this command is read-only
