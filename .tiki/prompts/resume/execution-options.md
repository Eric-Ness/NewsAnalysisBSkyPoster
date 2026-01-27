# Resume: Execution Options

Reference this document when continuing execution after resuming paused work.

## Option A: Continue in Current Context

If the remaining work is small and context allows, continue directly:

```
Continuing Phase 2...

Based on the saved context, I need to:
1. Add unit tests for the login endpoint
2. Add integration tests

[Proceeds with implementation]
```

**When to use Option A:**
- Remaining tasks are simple and well-defined
- Current context window has sufficient space
- No complex dependencies on previous work

## Option B: Spawn Sub-Agent

If the remaining work is substantial, spawn a sub-agent with full context using Task tool:

```
You are resuming Phase 2 of 3 for Issue #34: Add user authentication

## Project Context
<CLAUDE.md contents>

## Previous Phase Summaries
- Phase 1: Setup auth middleware - Created JWT validation middleware

## Current Phase: Add login endpoint

<original phase content>

## Progress Already Made
The following was completed before pause:
- Created login route at src/routes/auth.ts
- Implemented password validation in src/services/auth.ts
- Added JWT generation

## Remaining Tasks
- Add unit tests
- Add integration tests

## Decisions Already Made
- Used bcrypt for password hashing (industry standard)
- JWT expires in 24 hours

## Notes From Previous Session
Auth service needs error handling for edge cases

## Instructions
1. Continue from where we left off
2. Complete the remaining tasks listed above
3. Run tests to verify everything works
4. Provide a summary when done with "SUMMARY:" prefix
```

**When to use Option B:**
- Remaining work is substantial
- Multiple files need modification
- Complex logic or testing required

## Completion Handling

When the resumed phase completes:

1. Update phase to `completed` with summary
2. Delete the context file (no longer needed)
3. Continue to next phase or complete execution

```
Phase 2 complete: Add login endpoint
Summary: Added comprehensive tests for login endpoint, fixed edge case handling

Context file cleaned up.
Continuing to Phase 3...
```

## State File Updates

After completion, update `.tiki/state/current.json`:
- Increment `currentPhase`
- Add phase number to `completedPhases`
- Update `lastActivity`

Delete `.tiki/context/issue-N-phase-M.json` after successful completion.
