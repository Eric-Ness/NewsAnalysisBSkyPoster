---
type: prompt
name: tiki:commit
description: Create Tiki-aware git commits that reference the active issue and phase. Use when committing work during issue execution.
allowed-tools: Read, Bash, Glob
argument-hint: ["commit message"] [--no-state]
---

# Commit

Create git commits with Tiki awareness: references active issue and phase.

## Usage

```
/tiki:commit
/tiki:commit "Add login validation"
/tiki:commit --no-state
```

## Instructions

### Step 1: Check Tiki State

Read `.tiki/state/current.json` for activeIssue, currentPhase.

If state exists, read `.tiki/plans/issue-N.json` for phase title and total phases.

### Step 2: Check and Stage Changes

Read `.tiki/prompts/commit/staging-workflow.md` for the staging flow.

Run `git status --porcelain` to check for changes.

If no changes: Display "No changes to commit." and exit.

If unstaged changes exist, present them and ask what to stage.

### Step 3: Generate Commit Message

Read `.tiki/prompts/commit/message-format.md` for format and guidelines.

Include issue reference and phase context if Tiki state exists.

Use user-provided message as description if argument given.

### Step 3.5: Pre-Commit Hook (Conditional)

**Only execute if:** `.tiki/hooks/pre-commit` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `pre-commit` hook with:
- `TIKI_ISSUE_NUMBER`: Active issue number (if any)
- `TIKI_PHASE_NUMBER`: Current phase number (if any)
- `TIKI_COMMIT_MESSAGE`: Proposed commit message

If hook fails (non-zero exit or timeout), abort commit and show error message.

### Step 4: Confirm and Execute

Show proposed commit message and files to be committed.

Confirm with user: "Proceed with commit? [Y/n/e(dit)]"

Execute using HEREDOC format:
```bash
git commit -m "$(cat <<'EOF'
<commit message>
EOF
)"
```

### Step 5: Update State

Unless `--no-state` flag is passed:

- Get commit hash from `git rev-parse HEAD`
- Add commit to phase's `commits` array in plan file

### Step 5.5: Post-Commit Hook (Conditional)

**Only execute if:** `.tiki/hooks/post-commit` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `post-commit` hook with:
- `TIKI_ISSUE_NUMBER`: Active issue number (if any)
- `TIKI_PHASE_NUMBER`: Current phase number (if any)
- `TIKI_COMMIT_SHA`: Commit hash from `git rev-parse HEAD`

**Note:** Post-commit failure logs warning but doesn't fail (commit already done).

### Step 6: Display Result

Display result and next steps.

## Notes

- Always reference issue number for traceability
- Use `--no-state` to commit without updating Tiki tracking
- Phase info in commit body helps with git history analysis
- For examples, read `.tiki/prompts/commit/examples.md`
