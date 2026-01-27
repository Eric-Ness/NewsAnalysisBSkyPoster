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
/tiki:heal
/tiki:heal 34
/tiki:heal 34 --phase 2
/tiki:heal --dry-run       # Analyze without fixing
```

## Instructions

### Step 1: Identify Failed Phase

If no arguments, check for failed phases:

1. Read `.tiki/state/current.json`
2. Read `.tiki/plans/issue-*.json` for phases with `status: "failed"`

If no failed phase found:
```
No failed phases found.

Use `/tiki:state` to see current status.
```

### Step 2: Gather Error Context

Read the failed phase information:

```json
{
  "number": 2,
  "title": "Add login endpoint",
  "status": "failed",
  "error": {
    "type": "typescript",
    "message": "Property 'user' does not exist on type 'Request'",
    "file": "src/routes/auth.ts",
    "line": 45
  },
  "failedAt": "2026-01-10T11:45:00Z"
}
```

### Step 3: Analyze the Error

Perform diagnosis based on error type:

#### TypeScript/Compilation Errors

```bash
# Run TypeScript compiler to get full error
npx tsc --noEmit 2>&1 | head -50
```

#### Test Failures

```bash
# Run tests to see failures
npm test 2>&1 | tail -100
```

#### Runtime Errors

Read error logs, stack traces from the phase output.

#### Build Errors

```bash
npm run build 2>&1
```

### Step 4: Display Diagnosis

```
## Heal Analysis: Issue #34, Phase 2

### Error Summary
**Type:** TypeScript compilation error
**File:** src/routes/auth.ts:45
**Message:** Property 'user' does not exist on type 'Request'

### Root Cause Analysis
The `Request` type from Express doesn't include a `user` property by default.
This was added by the auth middleware in Phase 1, but TypeScript doesn't know about it.

### Suggested Fixes

#### Option 1: Extend Request type (Recommended)
Add type declaration to include `user` on Request:

```typescript
// src/types/express.d.ts
import { User } from './user';

declare global {
  namespace Express {
    interface Request {
      user?: User;
    }
  }
}
```

#### Option 2: Use type assertion
Cast the request in the handler:

```typescript
const user = (req as AuthenticatedRequest).user;
```

---
**Apply fix?** [Option 1] [Option 2] [Manual fix] [Skip phase]
```

### Step 5: Apply Fix

Based on user selection or automatic choice:

#### Automatic Fix

If the fix is straightforward and low-risk:

```
Applying fix: Extend Request type

Creating src/types/express.d.ts...
Updating tsconfig.json to include type declarations...

Verifying fix...
```

Run verification:
```bash
npx tsc --noEmit
```

If verification passes:
```
Fix applied successfully.

TypeScript compilation: PASS

Ready to retry phase?
- Retry: `/tiki:execute 34 --from 2`
- Review changes first: `git diff`
```

If verification fails:
```
Fix did not resolve the issue.

New error: [error details]

Options:
- Try alternative fix
- Manual intervention needed
- Skip this phase: `/tiki:skip-phase 2`
```

### Step 6: Update State

After successful fix:

Update phase status to `pending` (ready for retry):
```json
{
  "number": 2,
  "status": "pending",
  "error": null,
  "healedAt": "2026-01-10T12:00:00Z",
  "healAction": "Extended Request type with user property"
}
```

## Error Type Handlers

### TypeScript Errors

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `Property X does not exist on type Y` | Missing type definition | Add to interface or use declaration merging |
| `Cannot find module` | Missing import or package | Add import or install package |
| `Type X is not assignable to type Y` | Type mismatch | Fix types or add type assertion |
| `Object is possibly undefined` | Null safety | Add null check or optional chaining |

### Test Failures

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `Expected X but received Y` | Logic error | Fix implementation |
| `Cannot read property of undefined` | Missing mock or setup | Add test setup |
| `Timeout` | Async issue | Add await or increase timeout |

### Build Errors

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `Module not found` | Missing dependency | npm install |
| `Syntax error` | Invalid code | Fix syntax |
| `Out of memory` | Build too large | Increase memory or split |

### Runtime Errors

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `ENOENT` | File not found | Create file or fix path |
| `ECONNREFUSED` | Service not running | Start service |
| `Permission denied` | Access issue | Fix permissions |

## Heal Strategies

### Strategy 1: Direct Fix

For simple, obvious errors:
1. Identify the exact issue
2. Apply the fix directly
3. Verify the fix works
4. Mark phase as ready for retry

### Strategy 2: Spawn Diagnostic Agent

For complex errors, spawn a sub-agent:

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

### Strategy 3: User Intervention

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

Please investigate and run `/tiki:execute 34 --from 2` when ready.
```

## Dry Run Mode

With `--dry-run`, analyze without making changes:

```
## Heal Analysis (Dry Run)

### Would Apply
1. Create src/types/express.d.ts with Request extension
2. Update tsconfig.json to include types folder

### Verification
Would run: `npx tsc --noEmit`

No changes made. Run without --dry-run to apply fixes.
```

## Integration with Execute

When `/execute` encounters a phase failure:

1. Phase status set to `failed`
2. Error details saved to plan
3. Execution pauses
4. User prompted: "Phase failed. Use `/tiki:heal` to diagnose."

## Notes

- Heal is conservative - it prefers safe fixes over risky ones
- Complex fixes spawn a diagnostic agent for thorough analysis
- Always verify fixes before marking phase as ready
- Some errors genuinely need human judgment - don't force automation
- The goal is to unblock execution, not achieve perfection
