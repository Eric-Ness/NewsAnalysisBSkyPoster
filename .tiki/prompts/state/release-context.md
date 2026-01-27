# Release Context Lookup

Check if the active issue is part of any release and display release progress.

## Release Lookup Logic

1. **Glob for release files**: `.tiki/releases/*.json`

2. **Search each release for the active issue number**:

```javascript
for (const releaseFile of await glob('.tiki/releases/*.json')) {
  const release = readJSON(releaseFile);
  const issueInRelease = release.issues.find(i => i.number === activeIssue);
  if (issueInRelease) {
    releaseContext = {
      version: release.version,
      milestoneUrl: release.githubMilestone?.url || null,
      requirementsEnabled: release.requirementsEnabled,
      issues: release.issues,
      requirements: release.requirements || null
    };
    break;
  }
}
```

## Progress Calculation

```javascript
if (releaseContext) {
  const total = releaseContext.issues.length;
  const completed = releaseContext.issues.filter(i => i.status === 'completed').length;
  const inProgress = releaseContext.issues.filter(i => i.status === 'in_progress').length;
  releaseContext.progress = {
    total,
    completed,
    inProgress,
    percent: total > 0 ? Math.round((completed / total) * 100) : 0
  };
}
```

## Display Format

When issue is in a release:

```text
### Active Release
**v1.1** - 2/5 issues complete (40%)
| Issue | Title | Status | Phase |
|-------|-------|--------|-------|
| #34 | Add user authentication | in_progress | 2/3 |
| #35 | Fix login redirect | completed | - |
| #36 | Update docs | planned | 0/2 |
| #37 | Add password reset | not_planned | - |
| #38 | Security audit | not_planned | - |

{If requirementsEnabled:}
Requirements: 3/8 implemented (38%)

{If milestoneUrl:}
Milestone: https://github.com/owner/repo/milestone/1
```

When no active release:

```text
### Active Release
None - This issue is not part of any release.
Tip: Use `/tiki:release-add <issue-number>` to assign it to a release.
```
