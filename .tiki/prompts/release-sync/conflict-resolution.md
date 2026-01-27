# Conflict Resolution

Handle status conflicts during two-way sync.

## Status Conflict Prompt

For each status mismatch in two-way mode, prompt:

```text
### Status Conflict: #{number}

Issue: {title}
- Tiki status: {tikiStatus}
- GitHub status: {githubStatus}

Which status should win?

1. **Tiki** - Update GitHub to match ({tikiStatus})
2. **GitHub** - Update Tiki to match ({githubStatus})
3. **Skip** - Leave both unchanged

Enter choice [1]:
```

Default to option 1 (Tiki wins) if user presses Enter.

## Apply Resolution

Based on user choice:

**Option 1 (Tiki wins):**
```bash
# Close or reopen on GitHub
gh issue close {number}  # if Tiki completed
gh issue reopen {number} # if Tiki not completed
```

**Option 2 (GitHub wins):**
```javascript
if (githubClosed) {
  tikiIssue.status = 'completed';
  tikiIssue.completedAt = new Date().toISOString();
} else {
  tikiIssue.status = 'in_progress';
  tikiIssue.completedAt = null;
}
```

**Option 3 (Skip):**
No changes for this issue.

## Batch Conflicts

If multiple conflicts (>3), offer batch resolution:

```text
{count} status conflicts found. Resolve:
1. All Tiki wins
2. All GitHub wins
3. Resolve individually

Enter choice [3]:
```
