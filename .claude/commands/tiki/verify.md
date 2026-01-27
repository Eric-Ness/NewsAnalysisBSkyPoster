---
type: prompt
name: tiki:verify
description: Run UAT verification for a completed issue. Use when you want to validate all phase verification items before shipping.
allowed-tools: Read, Bash, Glob, Grep, Write, AskUserQuestion
argument-hint: <issue-number> [--report] [--phase <n>]
---

# Verify

Run structured UAT verification for a completed or in-progress issue.

## Usage

```
/tiki:verify 34              # Verify issue #34
/tiki:verify 34 --report     # Generate UAT report file
/tiki:verify 34 --phase 2    # Verify specific phase only
```

## Instructions

### Step 1: Load Plan File

Read `.tiki/plans/issue-<number>.json`. If not found:
```
No plan found for issue #<number>.
Create a plan first with `/tiki:plan-issue <number>`
```

Extract:
- `issue`: Issue metadata (number, title, url)
- `phases`: Array with `verification` arrays
- `successCriteria`: Overall success criteria

Build verification checklist from all phases (or filter by `--phase <n>` if provided).

### Step 2: Display Verification Checklist

Show items grouped by phase:

```
## Verification Checklist for Issue #34

Issue: Add user authentication
Status: in_progress (Phase 3 of 3)

### Phase 1: Setup database models (completed)
1. [ ] User model exists in src/models/user.ts
2. [ ] Session model has proper relationships

### Phase 2: Add authentication endpoints (completed)
3. [ ] POST /auth/login returns JWT token
4. [ ] Tests pass for auth endpoints

Total: N verification items across M phases
```

### Step 3: Run Automated Verifications

**IF** any verification items can be automated (file existence, content checks, test execution, build checks):

Read `.tiki/prompts/verify/automated-tests.md` for classification rules and execution logic.

Classify each item, run automated checks where possible, display results.

### Step 4: Interactive Manual Verification

**IF** any items are classified as manual (cannot be automatically verified):

Read `.tiki/prompts/verify/manual-verification.md` for interactive prompt workflow.

Use AskUserQuestion for each manual item with Pass/Fail/Skip/Need Info options.

### Step 5: Track and Display Results

**IF** any failures, skips, or pending items exist:

Read `.tiki/prompts/verify/failure-handling.md` for result tracking and recommendations.

Build summary with pass/fail counts, list items needing attention, provide recommendation based on pass rate.

**IF all items passed:** Display "All verifications passed. Ready to ship!"

### Step 6: Generate Report (--report flag)

**IF** `--report` flag provided:

Create `.tiki/reports/uat-issue-<number>.json` with full verification results.

Display summary table with report file location.

### Step 7: Offer Next Steps

Check `.tiki/config.json` - if `workflow.showNextStepMenu` is `false`, skip.

**All passed:** Offer Ship (Recommended), Re-verify, Done for now

**Some failed:** Offer View failures, Re-verify, Ship anyway, Done for now

Use AskUserQuestion for selection, invoke appropriate Skill if selected.

---

## Notes

- Run after completing all phases but before `/tiki:ship`
- Automated verification is best-effort
- Manual items require user interaction via AskUserQuestion
- UAT reports stored in `.tiki/reports/` for audit trail
- Use `--phase` to focus on specific phase during development
