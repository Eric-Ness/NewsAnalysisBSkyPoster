# Resume: Context Verification

Reference this document when verifying file state and displaying context summary for resume operations.

## File State Verification

Check that files mentioned in context still exist and have not been modified unexpectedly:

```bash
git status
```

### Conflict Handling

If there are conflicts or unexpected changes:

```
## Context Conflict

Files have changed since pause:
- src/routes/auth.ts (modified externally)

Options:
1. Continue anyway (may need to reconcile changes)
2. Reset to paused state: `git checkout src/routes/auth.ts`
3. Review changes first: `git diff src/routes/auth.ts`

Continue with resume? [y/n]
```

## Context Summary Display

Show the user what was happening when work was paused:

```
## Resuming Issue #34: Add user authentication

### Paused State
- **Phase:** 2 of 3 - Add login endpoint
- **Paused:** 2 hours ago
- **Reason:** User requested pause

### Progress When Paused
**Completed:**
- Created login route
- Implemented password validation
- Added JWT generation

**Remaining:**
- Add unit tests
- Add integration tests

### Decisions Made
- Used bcrypt for password hashing (industry standard)
- JWT expires in 24 hours

### Notes
Auth service needs error handling for edge cases

### Previous Phases
- Phase 1: Setup auth middleware - Created JWT validation middleware

---
Continuing execution...
```

## Verification Checklist

1. Verify `filesModified` from context exist
2. Verify `filesCreated` from context exist
3. Check for uncommitted changes in those files
4. Report any discrepancies to user before continuing
