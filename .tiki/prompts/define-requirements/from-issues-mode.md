# From-Issues Mode Workflow

**Load condition:** `--from-issues` flag provided

This prompt handles seeding requirements directly from open GitHub issues.

## Behavior Changes

When `--from-issues` flag is present:
1. **Skip Codebase Analysis**: Step 4 is completely skipped
2. **Focus on Issues Only**: Requirements generated exclusively from open issues
3. **Direct Mapping**: Each issue becomes a pending requirement

## Step 1: Fetch Open Issues

```bash
gh issue list --state open --json number,title,body,labels --limit 50
```

**If gh command fails:** Prompt user to authenticate or continue without issues.

**Categorize issues by labels:**

| Label Pattern | Category |
|---------------|----------|
| feature, enhancement, request | Feature requests |
| bug, defect, fix | Bug reports |
| tech-debt, refactor, cleanup | Technical debt |
| docs, documentation | Documentation |
| (no match) | Other |

## Step 2: Issue-to-Requirement Mapping

For each open GitHub issue:

### 2a: Generate Requirement Text
- Use issue title as base
- Prefix with "System shall " if not present
- Example: "Add dark mode" -> "System shall add dark mode functionality"

### 2b: Map Labels to Categories

| Label | Category |
|-------|----------|
| bug, defect, fix | QUAL |
| enhancement, feature, feat | CORE |
| docs, documentation | DOC |
| security, auth | SEC |
| performance, perf, speed | PERF |
| (no match) | CORE |

### 2c: Extract Verification from Issue Body

Search issue body in order:
1. "Acceptance Criteria" section -> use as verification
2. "Expected behavior" section -> use as verification
3. Checkbox items `- [ ]` -> combine as verification steps
4. If none found -> generate: "Verify {issue title} works as described"

### 2d: Set Metadata
- Status: `pending`
- implementedBy: `[issue_number]`

## Example Output

```json
{
  "id": "CORE-01",
  "text": "System shall add dark mode toggle",
  "category": "CORE",
  "verification": {
    "type": "manual_test",
    "description": "Toggle switches between light and dark themes"
  },
  "status": "pending",
  "implementedBy": [42],
  "evidence": ["Issue #42: Add dark mode toggle"]
}
```

## Workflow Summary

```
1. Parse --from-issues flag
2. Fetch open GitHub issues
3. Skip codebase analysis (Step 4)
4. Map each issue to requirement using rules above
5. Continue with interactive refinement (Step 6)
```

## Display Issue Summary

After fetching, show:

```
## GitHub Issues Loaded

Found N open issues:
- X Feature requests
- Y Bug reports
- Z Tech debt items
- W Documentation tasks
- V Other/uncategorized

These will be mapped directly to requirements.
```
