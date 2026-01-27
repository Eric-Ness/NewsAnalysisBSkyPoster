---
type: prompt
name: tiki:ship
description: Close out a completed issue by committing, pushing, and closing the GitHub issue. Use when you're done with an issue.
allowed-tools: Read, Bash, Glob, Write
argument-hint: [--no-push] [--no-close]
---

# Ship

Wrap up a completed issue: commit any remaining changes, push to remote, and close the GitHub issue.

## Usage

```
/tiki:ship
/tiki:ship --no-push    # Commit but don't push
/tiki:ship --no-close   # Commit and push but don't close the issue
```

## Instructions

### Step 1: Check Tiki State

Read `.tiki/state/current.json` to get the active issue:

```json
{
  "activeIssue": 34,
  "currentPhase": 3,
  "status": "in_progress"
}
```

If no active issue:
```
No active Tiki issue found.

Use /tiki:get-issue to start working on an issue first.
```

Also read the plan file `.tiki/plans/issue-<N>.json` to get issue details and verify all phases are complete.

### Step 2: Verify Phase Completion

Check that all phases are marked as completed in the plan file.

If any phases are not complete:
```
## Incomplete Phases

The following phases are not yet complete:
- Phase 2: Add login endpoint (in_progress)
- Phase 3: Add tests (pending)

Complete all phases before shipping, or use /tiki:skip-phase to skip remaining work.
```

### Step 3: Check for Uncommitted Changes

```bash
git status --porcelain
```

If there are uncommitted changes:

```
## Uncommitted Changes Detected

The following files have changes:
 M src/routes/auth.ts
 M tests/auth.test.ts
 A src/middleware/jwt.ts

Stage and commit these changes? [Y/n]
```

If user confirms, stage and commit with a closing message:

```bash
git add .
git commit -m "$(cat <<'EOF'
feat: Complete issue #34 - Add user authentication

Final changes for issue completion.
- <summary of remaining changes>

Closes #34
EOF
)"
```

If no changes to commit, skip to Step 4.

### Step 4: Push to Remote

Unless `--no-push` flag is present:

```bash
git push
```

Report result:
```
Pushed to origin/main
```

If push fails:
```
Push failed. You may need to pull first:
  git pull --rebase origin main

Then run /tiki:ship again.
```

### Step 5: Close GitHub Issue

Unless `--no-close` flag is present:

```bash
gh issue close <issue-number> --comment "Completed and shipped! 🚀"
```

If `gh` is not available or fails:
```
Could not close issue automatically.
Please close issue #34 manually at:
https://github.com/<owner>/<repo>/issues/34
```

### Step 6: Clean Up Tiki State

Update `.tiki/state/current.json` to clear the active issue:

```json
{
  "activeIssue": null,
  "currentPhase": null,
  "status": "idle",
  "lastCompletedIssue": 34,
  "lastCompletedAt": "2026-01-14T15:30:00Z"
}
```

Update the plan file status:

```json
{
  "issue": 34,
  "status": "shipped",
  "shippedAt": "2026-01-14T15:30:00Z"
}
```

### Step 7: Report Results

Display a summary:

```
## Shipped! 🚀

Issue #34: Add user authentication

Summary:
- 3 phases completed
- 5 commits made
- Issue closed on GitHub

Git log for this issue:
  abc1234 feat(auth): Add user model (#34)
  def5678 feat(auth): Add login endpoint (#34)
  ghi9012 test(auth): Add authentication tests (#34)
  jkl3456 feat: Complete issue #34 - Add user authentication

Ready for next issue? Run /tiki:whats-next
```

---

## Examples

### Example 1: Clean Ship

```
> /tiki:ship

## Shipping Issue #34

Checking state... Active issue: #34 (Add user authentication)
Checking phases... All 3 phases complete ✓
Checking changes... Working tree clean ✓

Pushing to origin...
Pushed to origin/main ✓

Closing issue #34...
Issue #34 closed ✓

Cleaning up state...
State cleared ✓

## Shipped! 🚀

Issue #34: Add user authentication

Summary:
- 3 phases completed
- 4 commits made
- Issue closed on GitHub

Ready for next issue? Run /tiki:whats-next
```

### Example 2: Ship with Uncommitted Changes

```
> /tiki:ship

## Shipping Issue #35

Checking state... Active issue: #35 (Fix login redirect)
Checking phases... All phases complete ✓
Checking changes... Uncommitted changes found

## Uncommitted Changes

 M src/routes/auth.ts
 M tests/redirect.test.ts

Stage and commit? [Y/n]
> Y

Committing...
Committed: xyz7890
feat: Complete issue #35 - Fix login redirect

Pushing to origin...
Pushed to origin/main ✓

Closing issue #35...
Issue #35 closed ✓

## Shipped! 🚀
```

### Example 3: Ship Without Push

```
> /tiki:ship --no-push

## Shipping Issue #36

Checking state... Active issue: #36
Checking phases... All phases complete ✓
Checking changes... Working tree clean ✓

Skipping push (--no-push flag)

Closing issue #36...
Issue #36 closed ✓

## Shipped! 🚀

Note: Changes not pushed. Run `git push` when ready.
```

### Example 4: Incomplete Phases

```
> /tiki:ship

## Shipping Issue #37

Checking state... Active issue: #37
Checking phases... INCOMPLETE

## Cannot Ship - Incomplete Phases

- Phase 1: Setup database ✓
- Phase 2: Add API endpoints (in_progress)
- Phase 3: Add tests (pending)

Options:
1. Complete remaining phases with /tiki:execute
2. Skip remaining phases with /tiki:skip-phase 2
3. Force ship anyway (not recommended)

Would you like to skip remaining phases? [y/N]
```

---

## Error Handling

### No Active Issue
```
No active Tiki issue found.

Start working on an issue first:
  /tiki:get-issue <number>
  /tiki:whats-next
```

### Push Fails
```
Push failed: rejected (non-fast-forward)

Your branch is behind origin. Options:
1. Pull and rebase: git pull --rebase origin main
2. Force push (if safe): git push --force-with-lease

After resolving, run /tiki:ship again.
```

### GitHub CLI Not Available
```
Could not close issue: GitHub CLI (gh) not found.

Install GitHub CLI: https://cli.github.com/

Or close the issue manually:
https://github.com/<owner>/<repo>/issues/34
```

### Not Authenticated
```
Could not close issue: Not authenticated with GitHub.

Run: gh auth login

Then try /tiki:ship again.
```

---

## Notes

- Ship is the final step in the Tiki workflow
- Always verifies phases are complete before shipping
- Creates a clear record of issue completion
- Cleans up state so you're ready for the next issue
- The "Closes #N" in commit messages auto-closes issues on push (GitHub feature)
