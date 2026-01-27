---
type: prompt
name: tiki:audit-plan
description: Validate a plan before execution. Use when you want to check phase sizes, dependencies, file conflicts, and verification steps before running /execute.
allowed-tools: Read, Glob, Grep
argument-hint: [issue-number] [--verbose]
---

# Audit Plan

Validates a plan before execution to identify potential issues.

## Usage

```
/tiki:audit-plan
/tiki:audit-plan 34
/tiki:audit-plan --verbose
```

## Instructions

### Step 1: Load the Plan

If no issue number provided, read `.tiki/state/current.json` to find active issue. Then read `.tiki/plans/issue-{number}.json`. If no plan found, inform user to run `/tiki:plan-issue`.

### Step 2: Run Validation Checks

#### Check 1: Phase Count and Sizes

Verify phases are reasonably sized:

- **Good:** 1-7 tasks, 1-10 files
- **Warning:** 8-10 tasks, 11-15 files
- **Error:** >10 tasks, >15 files

#### Check 2: Dependency Validation

Verify dependency integrity:

- Dependencies must reference earlier phases (lower numbers)
- No circular dependencies allowed
- Flag any forward dependencies as errors

#### Check 3: File Conflict Detection

Identify phases modifying same files:

- Sequential phases modifying same file: Info (expected)
- Non-adjacent phases: Warning (consider restructuring)
- Many phases same file: Error (should consolidate)

#### Check 4: Verification Steps

Each phase must have at least one verification step. Flag phases without verification as warnings.

#### Check 5: Referenced Files Exist

Check that files listed in phases exist (skip files marked `[new]` or `[create]`). Non-existent files are errors.

#### Check 6: Criteria Coverage

Validate all `successCriteria` are addressed by phases via `addressesCriteria`:

- **Error (0 phases):** Criterion not covered - blocking
- **Warning (1 phase):** Weak coverage - recommend adding more
- **Good (2+ phases):** Adequate coverage

### Step 3: Generate Report

Output format:
```
Plan Audit for Issue #{number}
========================
{symbol} {check result}
...

Recommendation: {based on results}
```

Symbols: `✓` passed, `⚠` warning, `✗` error

### Step 4: Provide Recommendation

- **All pass:** "Plan is ready. Run `/tiki:execute {issue}` to begin."
- **Warnings only:** "Review warnings. Plan can proceed, but consider adjustments."
- **Errors found:** "Plan has blocking issues. Run `/tiki:plan-issue {issue}` to revise."

### Step 5: Offer Next Steps

Read `.tiki/config.json`. If `workflow.showNextStepMenu` is false or errors exist, skip menu.

**All pass:** Use AskUserQuestion with:

- "Execute (Recommended)" → invoke `tiki:execute` with issue number
- "Discuss phases" → invoke `tiki:discuss-phases` with issue number
- "Done for now" → end

**Warnings only:** Use AskUserQuestion with:

- "Execute (Recommended)" → invoke `tiki:execute` with issue number
- "Discuss phases" → invoke `tiki:discuss-phases` with issue number
- "Re-plan" → invoke `tiki:plan-issue` with issue number
- "Done for now" → end

## Verbose Mode

With `--verbose`, read `.tiki/prompts/audit-plan/detailed-explanations.md` for extended output format including phase analysis, dependency graph, file modification map, and criteria coverage table.

## Fix Suggestions

When errors or warnings are found, read `.tiki/prompts/audit-plan/fix-suggestions.md` for resolution guidance.

## Notes

- Run audit before every `/tiki:execute` to catch issues early
- Warnings don't block execution but should be reviewed
- Errors must be resolved before execution can proceed
