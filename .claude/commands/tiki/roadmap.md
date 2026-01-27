---
type: prompt
name: tiki:roadmap
description: Generate a high-level project visualization across multiple releases, showing project progress, cross-issue relationships, and requirement coverage.
allowed-tools: Read, Bash, Glob, Write
argument-hint: [--output] [--include-archived] [--releases <versions>] [--format ascii|table]
---

# /tiki:roadmap - Project Roadmap Visualization

Generate a high-level view of the project across multiple releases.

## Usage

```
/tiki:roadmap                           # ASCII timeline (default)
/tiki:roadmap --output                  # Generate ROADMAP.md file
/tiki:roadmap --include-archived        # Include shipped/archived releases
/tiki:roadmap --releases v1.1,v1.2      # Filter to specific releases
/tiki:roadmap --format table            # Table-based view
```

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- `--output`: Write to ROADMAP.md instead of displaying
- `--include-archived`: Include `.tiki/releases/archive/*.json`
- `--releases <versions>`: Comma-separated version filter
- `--format ascii|table`: Output format (default: ascii)

## Step 2: Load Release Files

1. Glob `.tiki/releases/*.json` for active releases
2. If `--include-archived`, also glob `.tiki/releases/archive/*.json`
3. Read each JSON file and parse release data
4. If `--releases` filter provided, keep only matching versions

## Step 3: Sort and Organize

Sort releases by version (semver-aware):
- Compare major, minor, patch numerically
- Prereleases sort before releases

Group by status: active, upcoming, completed (if archived included).

## Step 4: Generate Output

Route to appropriate format generator based on flags.

### Format Selection

Based on flags, load and follow the appropriate format:

1. **If `--output` flag**:
   - Read `.tiki/prompts/roadmap/file-output.md`
   - Follow instructions to generate ROADMAP.md file
   - Also read `.tiki/prompts/roadmap/ascii-format.md` for the Overview section

2. **Else if `--format table`**:
   - Read `.tiki/prompts/roadmap/table-format.md`
   - Generate table-based output

3. **Else (default `--format ascii`)**:
   - Read `.tiki/prompts/roadmap/ascii-format.md`
   - Generate ASCII timeline output

## Helper Functions

### Status Symbols

| Status | Symbol |
|--------|--------|
| completed | ✓ |
| in_progress | ◐ |
| planned | ○ |
| not_planned | · |

### Version Comparison

Compare versions by: major > minor > patch > prerelease. Strip leading 'v'. Prereleases (e.g., `-beta`) sort before full releases.

### Progress Calculation

`progress = (completed_issues / total_issues) * 100`

## Empty State

If no release files found:

```
## No Releases Found

No releases have been created yet.

**Getting Started:**
1. Create a release: `/tiki:release-new v1.0`
2. Add issues to it: `/tiki:release-add <issue-number>`
3. View roadmap: `/tiki:roadmap`
```

## Requirements Coverage

If `.tiki/requirements.json` exists, include requirements coverage section:

| Requirement | Description | v1.0 | v1.1 |
|-------------|-------------|------|------|
| REQ-01 | Description | ✓ | |
| REQ-02 | Description | | ○ |

Symbols: `✓` implemented, `○` planned, empty = not linked.

If no requirements file exists, display setup instructions.

## Archive Handling

Archived releases (`.tiki/releases/archive/`) are shipped releases. Show with ship date:
`v1.0 (shipped 2026-01-10)`

## Filter Handling

When `--releases` filter active:
- Show "## Project Roadmap (Filtered)" header
- Add "Showing X of Y releases: v1.1, v1.2"
- Warn if requested version not found
