# Auto-Fix Strategies

Conditionally loaded when verification fails and `autoFix.enabled` is true.

## Error Classification

| Pattern | Type | Hint |
|---------|------|------|
| `Property 'X' does not exist` | type-error | Add property or fix name |
| `Cannot find module` | import-error | Install or fix path |
| `Type 'X' not assignable to 'Y'` | type-error | Fix mismatch |
| `Expected X received Y` | test-failure | Fix logic |
| `Module not found` | import-error | Fix dependency |
| `SyntaxError` | syntax-error | Fix syntax |
| `ENOENT` | runtime-error | Create file or fix path |
| `undefined` errors | runtime-error | Add null check |

Extract: error message, file, line, stack trace.

## 3-Tier Escalation

1. **Direct** (attempt 1) - Pattern-matched inline fix, no sub-agent
2. **Contextual Analysis** (attempt 2) - Diagnostic agent with git/file context
3. **Approach Review** (attempt 3) - Full issue context, can signal APPROACH_ISSUE

## Strategy: Direct Fix

Apply inline corrections based on error type:

| Type | Action |
|------|--------|
| type-error | Add property to interface or fix type |
| import-error | `npm install` or fix import path |
| syntax-error | Fix at indicated line |
| test-failure | Fix implementation logic |
| runtime-error | Add null check or create file |

## Strategy: Contextual Analysis

Spawn diagnostic agent via Task tool when direct fix fails.

**Gather context first:**
- Git diff: `git diff HEAD~3 -- {error_file}` (truncate if >150 lines)
- Related files: grep for imports of error file
- Phase files list from plan

**Diagnostic Agent Prompt:**
```
You are a diagnostic agent fixing Phase {N} of Issue #{number}.

## Error Context
- Type: {error_type}, Message: {error_message}
- File: {error_file}:{error_line}

## Git Changes (last 3 commits)
{git_diff_output}

## Related Files
{importing_files}

## Previous Attempts
{previous_attempts_summary}

## Instructions
1. Analyze root cause considering recent changes
2. Check type consistency across related files
3. Apply fix with progress indicators:
   - `Applying fix: {description}`
4. Output: AUTOFIX_RESULT: success|failure
   AUTOFIX_ACTION: {description}
   AUTOFIX_FILES: {files}
```

## Strategy: Approach Review

Spawn diagnostic agent with full issue context when contextual analysis fails.

**Approach Review Prompt:**
```
You are reviewing the implementation approach for Phase {N} of Issue #{number}.

## Issue Requirements
{issue_title}: {issue_body}
Success Criteria: {criteria_list}

## Phase Context
{phase_title}: {phase_content}

## Error
{error_type}: {error_message} at {error_file}

## Previous Attempts (all failed)
{fix_attempts_table}

## Instructions
Consider if the approach is fundamentally wrong. Output ONE of:

APPROACH_ISSUE: {explanation of why approach is wrong}
- Use when fixes keep failing for same root cause
- Use when implementation conflicts with requirements

OR

AUTOFIX_RESULT: success|failure
AUTOFIX_ACTION: {description}
AUTOFIX_FILES: {files}
```

## APPROACH_ISSUE Handling

When diagnostic agent outputs `APPROACH_ISSUE:`:

1. Record in fixAttempts with `verificationResult: "approach-issue"`
2. Include `approachIssueExplanation` field
3. Display notification and pause:

```
## Implementation Approach Issue Detected

Phase {N} has a fundamental approach problem.

Analysis: {explanation}

Options:
- Revise and retry: /tiki:execute {number} --from {N}
- Re-plan phase: /tiki:discuss-phases {number}
- Skip: /tiki:skip-phase {N}
```

## Recording Fix Attempts

Add to phase's `fixAttempts` array (schema: `.tiki/schemas/plan.schema.json`):

```json
{
  "id": "{NN}-fix-{MM}",
  "attemptNumber": N,
  "errorType": "...",
  "errorMessage": "...",
  "strategy": "direct|contextual-analysis|approach-review",
  "fixApplied": "...",
  "verificationResult": "pending|success|failure|approach-issue"
}
```

## Verification

After fix, run appropriate command:
- Type/syntax errors: `npx tsc --noEmit`
- Test failures: `npx jest {file}` or framework equivalent
- Build errors: `npm run build`

Display: `Re-running verification...` then `All verifications passed` or `Verification failed: {error}`

## Result Handling

**Success:** Update record, log `Auto-fix successful`, continue to next phase
**Failure with retries:** Escalate strategy, loop back
**Exhausted:** Display attempt summary, offer manual intervention options
