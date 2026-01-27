# Release Comparison Mode

Compare status and progress across multiple releases.

## Prerequisites

Load when user specifies multiple versions (e.g., `/tiki:release-status v1.1 v1.2`).

## Parse Multiple Versions

Extract all version arguments:
```text
Arguments: $ARGUMENTS
Split by spaces, each is a version to compare
```

## Load Each Release

For each version:
```bash
VERSION="${version}"
[[ ! "$VERSION" =~ ^v ]] && VERSION="v${VERSION}"
cat ".tiki/releases/${VERSION}.json" 2>/dev/null || \
cat ".tiki/releases/archive/${VERSION}.json" 2>/dev/null
```

## Build Comparison Table

```text
## Release Comparison

| Metric | v1.0 | v1.1 | v1.2 |
|--------|------|------|------|
| Status | shipped | active | active |
| Created | 2026-01-01 | 2026-01-10 | 2026-01-15 |
| Total Issues | 5 | 8 | 3 |
| Completed | 5 (100%) | 5 (63%) | 0 (0%) |
| In Progress | 0 | 1 | 1 |
| Requirements | 10/10 | 8/12 | 0/5 |
```

## Visual Progress Comparison

```text
### Progress Comparison

v1.0 ██████████ 100% (shipped)
v1.1 ██████░░░░ 63%
v1.2 ░░░░░░░░░░ 0%
```

## Issue Overlap Analysis

If comparing active releases, show shared issues:

```text
### Issue Distribution

Issues appearing in multiple releases:
- #42: In v1.1 (completed), v1.2 (planned)

Unique to v1.1: #34, #35, #36
Unique to v1.2: #50, #51
```

## Recommendations

Based on comparison:
- **Ship first:** Suggest which release to prioritize for shipping
- **Dependencies:** Identify if releases have blocking relationships
- **Resource allocation:** Note if in-progress work spans releases
