# GitHub Milestone Sync

Create and sync a GitHub milestone for the release.

## Check for Existing Milestone

```bash
gh api repos/:owner/:repo/milestones --jq '.[] | select(.title=="'${VERSION}'")'
```

**If milestone exists:**

Prompt user:
1. Link to existing - Use this milestone for the release
2. Create new - Create with suffix (e.g., "v1.1-2")
3. Skip - Don't link to any milestone

**If no milestone exists, create one:**

```bash
gh api repos/:owner/:repo/milestones -f title="${VERSION}" -f state="open" -f description="Release ${VERSION}"
```

## Assign Issues to Milestone

For each selected issue:

```bash
gh issue edit ${issue_number} --milestone "${VERSION}"
```

Track success/failure for each assignment.

## Update Release File

Add milestone info to release JSON:

```json
{
  "githubMilestone": {
    "number": 5,
    "url": "https://github.com/owner/repo/milestone/5"
  }
}
```

## Output Format

```text
## Milestone Sync Results

Milestone: {version} ({url})

Issue assignment:
| Issue | Status |
|-------|--------|
| #42 | Assigned |
| #38 | Failed: Already assigned to v1.0 |

{n}/{total} issues assigned successfully.
```

Note for conflicts: Issues already assigned to other milestones need manual reassignment.
