---
type: prompt
name: tiki:release-status
description: Display release status and progress
allowed-tools: Bash, Read, Glob, Grep
argument-hint: [version] [version2...]
---

# Release Status

Display release status and progress. Shows all active releases when no version specified, or detailed view of specific release(s).

**Usage:**
```text
/tiki:release-status           # Show all active releases summary
/tiki:release-status v1.1      # Show detailed status of specific release
/tiki:release-status v1.1 v1.2 # Compare multiple releases
```

## State Files

**Active releases:** `.tiki/releases/<version>.json`
**Archived releases:** `.tiki/releases/archive/<version>.json`

Fields: version, createdAt, status, requirementsEnabled, githubMilestone, issues[]

## Instructions

### Step 1: Parse Arguments

```text
Arguments: $ARGUMENTS
```

Determine mode:

- No arguments -> All releases summary
- Single version -> Detailed view
- Multiple versions -> Comparison mode

### Step 2: Route to Appropriate View

**No version specified:** Continue to All Releases View below.

**Single version:** Load `.tiki/prompts/release-status/detailed-view.md` for comprehensive status.

**Multiple versions:** Load `.tiki/prompts/release-status/comparison-mode.md` for side-by-side comparison.

---

## All Releases View

### Step A1: Scan for Active Releases

```bash
ls .tiki/releases/*.json 2>/dev/null || echo "NO_RELEASES"
```

If no releases found:
```text
## No Active Releases

No active releases found.
Create: /tiki:release-new <version>
View archived: ls .tiki/releases/archive/
```

### Step A2: Load and Calculate Metrics

For each release file, calculate:
- Issue completion: completed/total and percentage
- Requirements (if enabled): implemented/total and percentage

### Step A3: Display Summary Table

```text
## Active Releases

| Version | Issues | Progress | Requirements | Created |
|---------|--------|----------|--------------|---------|
| v1.2    | 3/8    | ███░░░░░░░ 38% | 5/12 (42%) | 2026-01-15 |
| v1.1    | 5/5    | ██████████ 100% | 8/8 (100%) | 2026-01-10 |

Quick Actions:
- View detailed: /tiki:release-status <version>
- Add issue: /tiki:release-add <issue> --to <version>
- Ship: /tiki:release-ship <version>
```

### Step A4: Identify Ready-to-Ship

If any release at 100%:
```text
### Ready to Ship
| Version | Issues | Requirements |
|---------|--------|--------------|
| v1.1    | 5/5    | 8/8 verified |

Ship: /tiki:release-ship v1.1
```

---

## Single Release View

### Step S1: Load Release

```bash
VERSION="${version}"
[[ ! "$VERSION" =~ ^v ]] && VERSION="v${VERSION}"
cat ".tiki/releases/${VERSION}.json" 2>/dev/null || \
cat ".tiki/releases/archive/${VERSION}.json" 2>/dev/null || \
echo "NOT_FOUND"
```

If not found: List available releases, suggest `/tiki:release-new`.

### Step S2: Display Header

```text
## Release {version}

| Field | Value |
|-------|-------|
| Status | {active/shipped} |
| Created | {createdAt} |
| Milestone | {url or "None"} |
| Requirements | {Enabled/Disabled} |
```

### Step S3-S11: Detailed Analysis

**Condition:** Load `.tiki/prompts/release-status/detailed-view.md` for:

- Issue status refresh from GitHub/plans
- Progress visualization
- Issues table with phase progress
- Timeline visualization
- Next action suggestions

### Step S9: Requirements Coverage

**Condition:** If `release.requirementsEnabled`, load `.tiki/prompts/release-status/requirements-coverage.md` for requirements status table.

## Error Handling

- **Release not found:** List available, suggest closest match
- **No releases exist:** Guide to `/tiki:release-new`
- **GitHub CLI unavailable:** Use cached data with warning
- **Empty release:** Guide to `/tiki:release-add`
