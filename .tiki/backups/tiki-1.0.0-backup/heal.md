---
type: prompt
name: tiki:heal
description: Auto-diagnose and fix failed phases. Use when a phase fails and you want automatic analysis and repair.
allowed-tools: Read, Write, Bash, Task, Edit, Grep, Glob
argument-hint: [issue-number] [--phase <n>] [--dry-run]
---

# Heal

Analyze a failed phase, diagnose the problem, and attempt to fix it automatically.

## Usage

```
/tiki:heal [issue] [--phase <n>] [--dry-run]
```

## Instructions

### Step 1: Identify Failed Phase

1. Read `.tiki/state/current.json` and `.tiki/plans/issue-*.json`
2. Find phases with `status: "failed"`
3. If none found: "No failed phases found. Use `/tiki:state` to see current status."

### Step 2: Gather Error Context

Extract from failed phase: error type, message, file, line number, timestamp.

### Step 3: Analyze the Error

Run appropriate diagnostic command based on error type:

- **TypeScript:** `npx tsc --noEmit 2>&1 | head -50`
- **Tests:** `npm test 2>&1 | tail -100`
- **Build:** `npm run build 2>&1`
- **Runtime:** Read error logs and stack traces

Read `.tiki/prompts/heal/error-handlers.md` for error type patterns and fixes.

### Step 4: Check Debug History

1. Read `.tiki/debug/index.json` if it exists
2. Search for resolved sessions matching error patterns
3. Include relevant past solutions in diagnosis output

### Step 5: Display Diagnosis

```
## Heal Analysis: Issue #N, Phase M

### Error Summary
**Type:** [error type]
**File:** [file:line]
**Message:** [error message]

### Root Cause Analysis
[Analysis of why the error occurred]

### Suggested Fixes
[Options with code examples]

**Apply fix?** [Option 1] [Option 2] [Manual fix] [Skip phase]
```

### Step 6: Apply Fix

Read `.tiki/prompts/heal/strategies.md` for fix approach selection.

1. Apply the selected fix
2. Run verification (e.g., `npx tsc --noEmit`)
3. If passes: Report success, suggest `/tiki:execute <issue> --from <phase>`
4. If fails: Report new error, offer alternatives or manual intervention

### Step 7: Update State

After successful fix, update phase in plan file:

- Set `status: "pending"`
- Clear `error`
- Add `healedAt` timestamp and `healAction` description

## Dry Run Mode

With `--dry-run`: Analyze and display diagnosis without applying fixes. Show what would be changed and what verification would run.

## Notes

- Prefer safe fixes over risky ones
- Complex fixes spawn a diagnostic agent via Task tool
- Always verify fixes before marking phase ready
- Some errors need human judgment - don't force automation
