# Sync Operations

Apply changes based on sync mode after differences are detected.

## Default Mode (Tiki -> GitHub)

Push Tiki state to GitHub milestone:

1. **Add Tiki-only issues to milestone:**
```bash
gh issue edit {number} --milestone "{VERSION}"
```

2. **Update status mismatches** (Tiki wins):
```bash
# If Tiki completed but GitHub open, close it
gh issue close {number}

# If Tiki not completed but GitHub closed, reopen
gh issue reopen {number}
```

3. **Display result:**
```text
## Sync Complete: Tiki -> GitHub

### Actions Taken
- Added #{number} to milestone {VERSION}
- {Closed/Reopened} #{number} to match Tiki status

Note: {githubOnlyCount} issues in GitHub but not in Tiki.
Use --pull to import them.
```

## Pull Mode (GitHub -> Tiki)

Pull GitHub state to Tiki release:

1. **Add GitHub-only issues to release:**
```javascript
release.issues.push({
  number: issue.number,
  title: issue.title,
  status: issue.state === 'closed' ? 'completed' : 'not_planned',
  requirements: [],
  currentPhase: null,
  totalPhases: null,
  completedAt: issue.state === 'closed' ? new Date().toISOString() : null
});
```

2. **Update status mismatches** (GitHub wins):
```javascript
if (githubClosed && !tikiClosed) {
  tikiIssue.status = 'completed';
  tikiIssue.completedAt = new Date().toISOString();
} else if (!githubClosed && tikiClosed) {
  tikiIssue.status = 'in_progress';
  tikiIssue.completedAt = null;
}
```

3. **Save updated release file** and display results.

## Two-Way Mode

Merge changes from both directions:

1. Add Tiki-only issues to GitHub milestone
2. Add GitHub-only issues to Tiki release
3. For status conflicts, load conflict-resolution.md and prompt user
4. Default: Tiki wins if user just presses Enter

Display combined results showing actions taken in both directions.
