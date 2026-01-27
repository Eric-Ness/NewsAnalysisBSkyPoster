# Heal Strategies

Three approaches for fixing failed phases, from simplest to most involved.

## Strategy 1: Direct Fix

For simple, obvious errors:

1. Identify the exact issue
2. Apply the fix directly
3. Verify the fix works
4. Mark phase as ready for retry

Use when: Error is clear, fix is straightforward, low risk of side effects.

## Strategy 2: Spawn Diagnostic Agent

For complex errors, spawn a sub-agent via Task tool:

```
You are diagnosing a failed phase.

## Error Context
<error details>

## Files Involved
<relevant files>

## Your Task
1. Analyze the error thoroughly
2. Identify the root cause
3. Propose a fix
4. Implement the fix
5. Verify it works

Report your findings and actions.
```

Use when: Root cause unclear, multiple files involved, or error requires investigation.

## Strategy 3: User Intervention

For errors requiring human judgment:

```
## Manual Intervention Needed

This error requires human decision:

**Error:** Database migration conflict
**Details:** Migration 003 conflicts with existing schema

**Options:**
1. Roll back migration 002 and reapply
2. Create a new migration to reconcile
3. Manually edit the schema

Please investigate and run `/tiki:execute <issue> --from <phase>` when ready.
```

Use when: Business logic decisions needed, irreversible operations, or ambiguous requirements.
