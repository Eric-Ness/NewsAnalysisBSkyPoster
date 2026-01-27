# Batch Add Mode

Handle adding multiple issues to a release in a single operation.

## Display Issues Table

```text
## Adding {count} Issues to Release {version}

| # | Title | Labels | Status |
|---|-------|--------|--------|
{For each validated issue}
```

## Batch Requirements Mapping

If `release.requirementsEnabled` and `requirements.json` exists:

```text
### Requirements Mapping

1. **Auto-map** - Accept suggested mappings for all issues
2. **Review each** - Approve/edit mapping per issue
3. **Skip all** - Add without requirement mapping

Enter choice:
```

### Auto-Map Flow

Generate suggestions using keyword matching on issue title/body/labels.

Display batch table:
```text
| # | Title | Suggested Requirements |
|---|-------|------------------------|
```

Confirm: Yes / Edit specific / Cancel

### Review Each Flow

For each issue, show single-issue requirements prompt from `requirements-linking.md`.

## Process All Issues

Build entries for all validated issues and add to release.

```text
## Issues Added

Successfully added {count} issue(s) to release {version}.

| # | Title | Status | Requirements |
|---|-------|--------|--------------|
```

## Notes

- Skip issues with validation errors, proceed with valid ones
- Report count: "{validCount} of {totalCount} issues added"
- If all issues fail validation, exit with error summary
