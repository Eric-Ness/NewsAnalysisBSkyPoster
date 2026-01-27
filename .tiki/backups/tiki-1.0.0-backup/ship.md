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

Read `.tiki/state/current.json` to get the active issue. If no active issue, inform user to run `/tiki:get-issue` first. Also read `.tiki/plans/issue-<N>.json` for issue details.

### Step 2: Verify Phase Completion

Check all phases are marked "completed" in the plan file. If incomplete phases exist, list them and suggest `/tiki:execute` to complete or `/tiki:skip-phase` to skip.

### Step 3: Check for Uncommitted Changes

Run `git status --porcelain`. If uncommitted changes exist, ask user to confirm staging and committing with a message that includes "Closes #N".

### Step 4: Push to Remote

Unless `--no-push` flag: run `git push`. If push fails (e.g., non-fast-forward), advise user to pull/rebase first.

### Step 5: Close GitHub Issue

Unless `--no-close` flag: run `gh issue close <N> --comment "Completed and shipped!"`. If gh fails, provide manual close URL.

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

- Set `activeIssue` and `currentPhase` to null
- Set `status` to "idle"
- Record `lastCompletedIssue` and `lastCompletedAt`

Update plan file: set `status` to "shipped" and add `shippedAt` timestamp.

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
