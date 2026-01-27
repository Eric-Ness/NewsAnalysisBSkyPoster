# Milestone Sync

Assign added issues to the GitHub milestone linked to this release.

## Check for Milestone

```bash
# From release data
MILESTONE_TITLE="${release.githubMilestone?.title}"
MILESTONE_NUMBER="${release.githubMilestone?.number}"
```

## Assign Issues

If milestone exists:

```bash
for issue_number in ${ISSUE_NUMBERS}; do
  gh issue edit ${issue_number} --milestone "${MILESTONE_TITLE}"
done
```

## Report Results

```text
### Milestone Sync

Assigning issues to milestone "{version}":

| Issue | Status |
|-------|--------|
| #23 | Assigned |
| #24 | Assigned |
| #25 | Failed: {reason} |

{successes}/{total} issues assigned.
```

## Handle Errors

- Failed assignments are warnings, not blockers
- Include specific error message per issue
- Continue with remaining issues on failure
- Provide manual fix command: `gh issue edit {N} --milestone "{title}"`

## No Milestone

If release has no linked milestone:
- Skip silently
- Do not prompt or report
