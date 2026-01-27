# Convert Todo to GitHub Issue

Handle --convert operation to create GitHub issue from todo.

## Workflow

1. **Normalize ID** (same as actions.md)

2. **Find todo** - Error if not found (show available IDs)

3. **Check if already converted:**
   ```
   Note: [todo-001] was already converted to Issue #42
   URL: https://github.com/owner/repo/issues/42
   ```

4. **Build issue body:**
   ```
   {todo.description}

   ---

   Converted from Tiki todo item

   - Original ID: {todo.id}
   - Priority: {todo.priority || 'medium'}
   - Created: {todo.createdAt}

   ---
   Converted via /tiki:list-todos --convert
   ```

5. **Create issue via gh CLI:**
   ```bash
   gh issue create --title "{todo.description}" --body "$(cat <<'EOF'
   {issue body}
   EOF
   )"
   ```

6. **Parse response** - Extract issue number and URL from output

7. **Update todo:**
   ```javascript
   todo.convertedToIssue = {
     number: issueNumber,
     url: issueUrl,
     convertedAt: new Date().toISOString()
   };
   todo.status = "completed";
   todo.completedAt = new Date().toISOString();
   ```

8. **Write** to `.tiki/todos.json`

9. **Display:**
   ```
   Creating GitHub issue...
   Converted: [todo-001] "Description" -> Issue #42
   URL: https://github.com/owner/repo/issues/42
   ```

## Error: gh CLI Failure

```
Error: Failed to create GitHub issue.

Possible causes:
- GitHub CLI (gh) is not installed. Install from: https://cli.github.com/
- Not authenticated. Run: gh auth login
- Not in a git repository with a GitHub remote

The todo has NOT been modified.
```
