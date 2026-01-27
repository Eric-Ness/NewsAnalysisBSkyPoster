# Skip Phase: Validation Checks

Reference this document when validating a skip request.

## Check 1: Phase Exists

Verify the phase number is valid for the issue.

```
Error: Phase 5 does not exist.

Issue #34 has 4 phases. Valid phase numbers: 1-4
```

## Check 2: Phase is Skippable

A phase can only be skipped if status is `pending` or `in_progress`.

```
Error: Cannot skip Phase 1 - it is already completed.

Phase statuses:
  1. Setup project structure [completed] - cannot skip
  2. Add authentication [in_progress] - can skip
  3. Add user dashboard [pending] - can skip

Completed phases cannot be skipped. Use /tiki:redo-phase 1 to redo.
```

For failed phases, warn but allow:

```
Phase 2 is marked as failed.

Error: TypeScript compilation error in src/auth.ts

Options:
1. Skip anyway (mark as skipped, ignore error)
2. Use /tiki:heal to attempt automatic fix
3. Cancel

> 1

Phase 2 skipped (was failed).
Note: The error was not resolved. Dependent phases may fail.
```

## Check 3: Dependency Warning

If other phases depend on this phase, warn but allow skip:

```
Warning: Phase 2 has dependents.

The following phases depend on Phase 2:
  - Phase 3: Add user dashboard (depends on auth)
  - Phase 4: Write tests (depends on auth)

Skipping may cause these phases to fail.

Continue? (y/n)
```

Check dependencies by examining `dependencies` array in each phase of the plan.
