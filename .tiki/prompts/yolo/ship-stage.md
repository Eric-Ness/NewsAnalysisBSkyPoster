# Ship Stage

Execute the ship workflow to commit, push, and close the issue.

## Instructions

1. **Verify all phases complete** - Check plan status

2. **Commit changes** (if uncommitted):
   ```bash
   git add .
   git commit -m "feat: <issue title> (#<number>)"
   ```

3. **Push to remote**:
   ```bash
   git push origin <branch>
   ```

4. **Close GitHub issue**:
   ```bash
   gh issue close <number> --comment "Shipped via /tiki:yolo"
   ```

5. **Version bump** (Tiki repo only):
   - Check for `version.json` in project root
   - If exists: increment patch version, add changelog entry
   - Commit and push version bump

6. **Clean up state**:
   - Clear `.tiki/state/current.json`

## Output Format

### Success

```text
[7/7] Shipping...
      Committing changes... OK
      Pushing to origin... OK
      Closing issue #<number>... OK
      Bumping version... OK (1.0.5 -> 1.0.6)  # If Tiki repo
      Cleaning up state... OK

---

## YOLO Complete!

Issue #<number>: <title>
All <N> phases completed successfully.
TDD: <enabled/disabled>
Queue: <N> items (or Empty)
Shipped: Yes

### Phase Summaries
- Phase 1: <summary>
- Phase 2: <summary>

### What Happened
- Code committed and pushed to origin
- GitHub issue #<number> closed
- Tiki state cleared

Ready for next issue? Run /tiki:whats-next
```

### Failure

```text
[7/7] Shipping... FAILED

<error description>

The issue was NOT closed. Options:
- Fix the issue and run `/tiki:ship` manually
- View state: `/tiki:state`
```

## Version Bump Details

For Tiki repo (`version.json` exists):

```json
{
  "version": "1.0.6",
  "date": "<YYYY-MM-DD>",
  "changes": [
    "Issue #<number>: <title summary>"
  ]
}
```
