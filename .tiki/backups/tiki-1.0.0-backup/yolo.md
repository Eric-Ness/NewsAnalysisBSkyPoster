---
type: prompt
name: tiki:yolo
description: Run the full Tiki workflow (get -> review -> plan -> audit -> execute -> review -> ship) with TDD enabled by default.
allowed-tools: Bash, Read, Write, Glob, Grep, Task, Edit, Skill
argument-hint: <issue-number> [--no-tdd] [--skip-review] [--force-review] [--no-ship]
---

# YOLO Mode

Execute the complete Tiki workflow pipeline for an issue in one command.

## Usage

```text
/tiki:yolo 34
/tiki:yolo 34 --no-tdd        # Skip TDD mode
/tiki:yolo 34 --skip-review   # Skip review step
/tiki:yolo 34 --force-review  # Continue despite blocking concerns
/tiki:yolo 34 --no-ship       # Skip auto-ship at end
```

## Instructions

### Step 0: Parse Arguments

```
issueNumber = args[0]  // Required
noTdd = args.includes('--no-tdd')
skipReview = args.includes('--skip-review')
forceReview = args.includes('--force-review')
noShip = args.includes('--no-ship')
```

If no issue number: Display usage and stop.

### Step 1: Progress Header

```text
## YOLO Mode: Issue #<number>

Mode: TDD <enabled|disabled>, Review <enabled|skipped>, Ship <enabled|disabled>

[1/7] Fetching issue...
```

Adjust step count: Default 7, minus 1 for `--skip-review`, minus 1 for `--no-ship`.

### Step 2: Fetch Issue

```bash
gh issue view <number> --json number,title,body,state,labels,assignees,milestone
```

If not found: Display error, stop. If found: Show title, state, labels, continue.

### Step 2.5: Review Stage (Conditional)

**If `--skip-review`:** Display "SKIPPED", continue to Step 3.

**Otherwise:** Read `.tiki/prompts/yolo/review-stage.md` and follow instructions.
- If verdict "blocked" and no `--force-review`: Stop execution
- Otherwise: Continue to Step 3

### Step 3: Create Plan

Run plan creation (same as `/tiki:plan-issue`):
1. Analyze issue content
2. Explore codebase
3. Break into phases
4. Create `.tiki/plans/issue-<number>.json`

If failed: Stop. If success: Show phase count and titles.

### Step 4: Audit Plan

Validate the plan (same as `/tiki:audit-plan`):
- Check phase sizes, dependencies, file conflicts
- Verify referenced files exist

If blocking errors: Stop. If warnings: Show and continue.

### Step 5: Execute Phases

Execute all phases (same as `/tiki:execute`):

**If TDD enabled:** Read `.tiki/prompts/yolo/tdd-handling.md` for TDD workflow.

For each phase:
1. Spawn sub-agent via Task tool
2. Extract summary and discovered items
3. Update state files
4. Report progress

If failed: Read `.tiki/prompts/yolo/error-recovery.md`, stop.

### Step 6: Review Queue

Check `.tiki/queue/pending.json` for discovered items. Display count and list if any.

### Step 7: Ship (Conditional)

**If `--no-ship`:** Display completion summary without shipping.

**Otherwise:** Read `.tiki/prompts/yolo/ship-stage.md` and follow ship workflow.

## Options

| Flag | Effect |
|------|--------|
| `--no-tdd` | Skip TDD mode (no test-first) |
| `--skip-review` | Skip pre-planning review |
| `--force-review` | Override blocking review concerns |
| `--no-ship` | Skip auto commit/push/close |

Combine flags: `/tiki:yolo 34 --no-tdd --skip-review`

Default pipeline (7 steps): fetch → review → plan → audit → execute → queue → ship

## Error Handling

On any step failure: Read `.tiki/prompts/yolo/error-recovery.md` for recovery options.

## Cleanup

After completion (success or failure):

```bash
rm -f ./tmpclaude-* ./nul ./NUL .tiki/tmp-* .tiki/*.tmp 2>/dev/null || true
```

## Notes

- Each step validates before proceeding
- Progress saved at each step (partial failures don't lose work)
- TDD enabled by default for quality
- State files updated throughout (`/tiki:state` shows progress)
- For more control, use individual commands: `/tiki:get-issue`, `/tiki:plan-issue`, `/tiki:execute`, `/tiki:ship`
