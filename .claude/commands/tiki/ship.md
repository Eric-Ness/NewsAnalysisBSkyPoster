---
type: prompt
name: tiki:ship
description: Close out a completed issue by committing, pushing, and closing the GitHub issue. Use when you're done with an issue.
allowed-tools: Read, Bash, Glob, Write, AskUserQuestion, Skill
argument-hint: [--no-push] [--no-close]
---

# Ship

Wrap up a completed issue: commit remaining changes, push to remote, and close the GitHub issue.

## Usage

```
/tiki:ship
/tiki:ship --no-push    # Commit but don't push
/tiki:ship --no-close   # Commit and push but don't close
```

## Instructions

### Step 1: Check Tiki State

Read `.tiki/state/current.json` to get the active issue.

**V2 Format Detection:**
- If `version` field equals `2` or `activeExecutions` array exists: use v2 format
- Otherwise: fall back to v1 format

**V2 State Handling:**
1. Check `activeExecutions` array for active execution (status != "completed")
2. If multiple active executions exist, use the one matching `activeIssue` (if set) or ask user to specify
3. Extract `issue` number from the execution object
4. Store execution `id` for later archival in Step 7

**V1 State Handling (fallback):**
1. Use `activeIssue` field directly
2. No execution ID to track

If no active issue found in either format, inform user to run `/tiki:get-issue` first. Also read `.tiki/plans/issue-<N>.json` for issue details.

### Step 2: Verify Phase Completion

Check all phases are marked "completed" in the plan file. If incomplete phases exist, list them and suggest `/tiki:execute` to complete or `/tiki:skip-phase` to skip.

### Step 2.5: Pre-Ship Hook (Conditional)

Check for hook file in order:
1. `.tiki/hooks/pre-ship` (no extension)
2. `.tiki/hooks/pre-ship.sh`
3. `.tiki/hooks/pre-ship.ps1`

**Only execute if:** one of the above files exists. Execute the first match found using the appropriate shell.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `pre-ship` hook with:
- `TIKI_ISSUE_NUMBER`: Active issue number
- `TIKI_ISSUE_TITLE`: Issue title (sanitized)

If hook fails (non-zero exit or timeout), abort ship and show error message.

### Step 3: Check for Uncommitted Changes

Run `git status --porcelain`. If uncommitted changes exist, ask user to confirm staging and committing with a message that includes "Closes #N".

### Step 4: Push to Remote

Unless `--no-push` flag: run `git push`. If push fails (e.g., non-fast-forward), advise user to pull/rebase first.

### Step 5: Close GitHub Issue

Unless `--no-close` flag: run `gh issue close <N> --comment "Completed and shipped!"`. If gh fails, provide manual close URL.

### Step 5.5: Post-Ship Hook (Conditional)

**Only execute if:** `.tiki/hooks/post-ship` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `post-ship` hook with:
- `TIKI_ISSUE_NUMBER`: Issue number
- `TIKI_ISSUE_TITLE`: Issue title (sanitized)
- `TIKI_COMMIT_SHA`: Final commit hash

**Note:** Post-ship failure logs warning but doesn't fail ship (work already done).

### Step 6: Bump Version (Tiki repo only)

**Condition:** Only if `.claude/commands/tiki/ship.md` exists (i.e., this IS the Tiki repo).

Read `.tiki/prompts/ship/version-bump.md` for version bump workflow.

### Step 6.5: Update Release Progress (Optional)

**Condition:** Only if issue is part of a release (check `plan.release` field or scan `.tiki/releases/*.json`).

Read `.tiki/prompts/ship/release-progress.md` for release tracking updates.

**Note:** This step should never cause ship to fail - all errors are warnings only.

### Step 6.7: Knowledge Capture (Optional)

**Condition:** Only if `.tiki/config.json` has `knowledge.captureOnShip: true` (default: true) AND plan has >= `knowledge.minPhasesForCapture` phases (default: 1).

Read `.tiki/prompts/ship/knowledge-synthesis.md` for knowledge synthesis workflow.

**Note:** This step should never cause ship to fail - all errors are warnings only.

### Step 7: Clean Up Tiki State

Update `.tiki/state/current.json`:

**V2 Format (if `version` equals 2 or `activeExecutions` exists):**
1. Find the execution in `activeExecutions` by its `id` (stored from Step 1)
2. Remove from `activeExecutions` array
3. Create archived execution object for `executionHistory`:
   ```json
   {
     "id": "<execution-id>",
     "issue": <issue-number>,
     "issueTitle": "<issue-title>",
     "status": "completed",
     "startedAt": "<original-startedAt>",
     "endedAt": "<current-timestamp>",
     "completedPhases": <count-of-completed-phases>,
     "totalPhases": <total-phases>,
     "summary": "Issue #N completed and shipped"
   }
   ```
4. Append to `executionHistory` array (create if doesn't exist)
5. Update top-level fields:
   - Set `lastCompletedIssue` to the issue number
   - Set `lastCompletedAt` to current timestamp
   - Set `lastActivity` to current timestamp
6. Update deprecated v1 fields for compatibility:
   - If no remaining active executions: set `activeIssue`, `currentPhase` to null, `status` to "idle"
   - If other active executions remain: set to next active execution's values

**V1 Format (fallback):**
- Set `activeIssue` and `currentPhase` to null
- Set `status` to "idle"
- Set `lastCompletedIssue` to the issue number
- Set `lastCompletedAt` to current timestamp

**Update plan file:** Set `status` to "shipped" and add `shippedAt` timestamp.

### Step 8: Report Results

Display summary including:

- Issue number and title
- Phases completed count
- Commits made
- Issue close status
- Version bump (if applicable)
- Release progress (if applicable, from Step 6.5)
- Knowledge captured (if applicable, from Step 6.7)

### Offer Next Steps

1. Read `.tiki/config.json`
2. If `workflow.showNextStepMenu` is `false`, skip this section
3. Use `AskUserQuestion` to present options:
   - "What's next" -> invoke `/tiki:whats-next`
   - "Get new issue" -> invoke `/tiki:get-issue`
   - "View state" -> invoke `/tiki:state`
   - "Done for now" -> end

## Error Handling

- **No active issue:** Direct to `/tiki:get-issue`
- **Push fails:** Suggest `git pull --rebase` then retry
- **gh not available:** Provide manual GitHub URL
- **Not authenticated:** Direct to `gh auth login`

## Notes

- "Closes #N" in commit messages auto-closes issues on push (GitHub feature)
- Ship verifies all phases complete before proceeding
- Cleans up state so you're ready for the next issue
