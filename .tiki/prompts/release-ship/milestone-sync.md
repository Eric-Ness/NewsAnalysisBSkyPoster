# Milestone Sync Workflow

Close the GitHub milestone linked to this release.

## Execution

Check if milestone is linked and close it:

```bash
MILESTONE_NUMBER="${release.githubMilestone?.number}"

if [ -n "${MILESTONE_NUMBER}" ]; then
  gh api repos/:owner/:repo/milestones/${MILESTONE_NUMBER} -X PATCH -f state="closed"
fi
```

## Handle Result

**Success:**
```
### Milestone Closed

GitHub milestone "{version}" (#{number}) has been closed.
URL: {release.githubMilestone.url}
```

**No milestone linked:**
```
### Milestone

No GitHub milestone linked to this release.
```

**API error:**
```
### Milestone Warning

Failed to close GitHub milestone: {error}

You may need to close it manually:
  gh api repos/:owner/:repo/milestones/{number} -X PATCH -f state="closed"
```

## Notes

- Milestone closure is non-blocking - errors are warnings only
- Report status regardless of outcome
- Include manual fix command on failure
