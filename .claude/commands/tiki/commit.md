---
type: prompt
name: tiki:commit
description: Create Tiki-aware git commits that reference the active issue and phase. Use when committing work during issue execution.
allowed-tools: Read, Bash, Glob
argument-hint: ["commit message"] [--no-state]
---

# Commit

Create git commits with Tiki awareness: references the active GitHub issue, notes which phase the commit relates to, and optionally updates phase state.

## Usage

```
/tiki:commit
/tiki:commit "Add login validation"
/tiki:commit --no-state          # Don't update phase state after commit
```

## Instructions

### Step 1: Check Tiki State

Read `.tiki/state/current.json` to check for active issue and phase:

```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "in_progress"
}
```

If state exists, also read the plan file `.tiki/plans/issue-34.json` to get phase details:

```json
{
  "phases": [
    {
      "number": 2,
      "title": "Add login endpoint",
      "status": "in_progress"
    }
  ]
}
```

### Step 2: Check for Staged Changes

```bash
git status --porcelain
```

If no changes staged or modified:
```
No changes to commit.

Use `git add <files>` to stage changes, or check `git status` for details.
```

### Step 3: Stage Changes

If there are unstaged changes, present them and ask what to stage:

```bash
git diff --stat
```

Display:
```
Changes not staged:
  src/routes/auth.ts    | 45 +++++++++++++++
  src/middleware/jwt.ts | 12 ++++
  tests/auth.test.ts    | 30 ++++++++++

Stage all changes? [Y/n] or specify files:
```

Stage based on user input:
```bash
git add .                    # If user confirms all
git add src/routes/auth.ts   # If user specifies files
```

### Step 4: Generate Commit Message

#### With Active Tiki Issue

Format:
```
<type>(<scope>): <description> (#<issue>)

Phase <N> of <total>: <phase title>
- <bullet point of what was done>
- <bullet point of what was done>
```

Example:
```
feat(auth): Add login endpoint (#34)

Phase 2 of 3: Add login endpoint
- Implemented POST /api/login
- Added JWT token generation
- Added input validation for email/password
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding tests
- `docs`: Documentation
- `chore`: Maintenance

#### Without Active Tiki Issue (Regular Commit)

If no Tiki state exists, create a standard commit:

```
<type>(<scope>): <description>

<optional body>
```

### Step 5: Confirm and Execute Commit

Display the proposed commit:

```
## Proposed Commit

**Message:**
feat(auth): Add login endpoint (#34)

Phase 2 of 3: Add login endpoint
- Implemented POST /api/login
- Added JWT token generation

**Files:**
- src/routes/auth.ts
- src/middleware/jwt.ts

Proceed with commit? [Y/n/e(dit)]
```

If confirmed:
```bash
git commit -m "$(cat <<'EOF'
feat(auth): Add login endpoint (#34)

Phase 2 of 3: Add login endpoint
- Implemented POST /api/login
- Added JWT token generation
EOF
)"
```

### Step 6: Update Phase State (Optional)

Unless `--no-state` is passed, update the plan file to record the commit:

Add to the phase in `.tiki/plans/issue-34.json`:

```json
{
  "number": 2,
  "title": "Add login endpoint",
  "status": "in_progress",
  "commits": [
    {
      "hash": "abc1234",
      "message": "feat(auth): Add login endpoint (#34)",
      "timestamp": "2026-01-10T11:30:00Z"
    }
  ]
}
```

### Step 7: Display Result

```
Committed: abc1234
feat(auth): Add login endpoint (#34)

Phase 2 of 3: Add login endpoint
- 3 files changed
- Commit recorded in phase state

Next: Continue implementation or run `/tiki:execute` to move to next phase
```

## Commit Message Guidelines

### Type Selection

| Type | When to Use |
|------|-------------|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug or issue |
| `refactor` | Restructuring code without changing behavior |
| `test` | Adding or updating tests |
| `docs` | Documentation changes |
| `chore` | Build, config, dependency updates |
| `style` | Formatting, whitespace (no code change) |

### Scope Selection

Use the area of the codebase being changed:
- `auth`, `api`, `db`, `ui`, `config`, `tests`, etc.

### Description Guidelines

- Start with lowercase verb (add, fix, update, remove)
- Keep under 50 characters
- Don't end with period

## Examples

### Example 1: Mid-Phase Commit

```
> /tiki:commit "Add JWT validation middleware"

## Checking Tiki State
Active: Issue #34 (Add user authentication)
Phase: 2 of 3 (Add login endpoint)

## Changes to Commit
 M src/middleware/jwt.ts
 M src/routes/auth.ts
 A tests/jwt.test.ts

## Proposed Commit
feat(auth): Add JWT validation middleware (#34)

Phase 2 of 3: Add login endpoint
- Created JWT validation middleware
- Integrated with auth routes
- Added unit tests

Proceed? [Y/n]

---

Committed: def5678
Commit recorded in phase 2 state.
```

### Example 2: No Active Issue

```
> /tiki:commit

## Checking Tiki State
No active Tiki issue.

## Changes to Commit
 M README.md

## Proposed Commit
docs: Update README with installation instructions

Proceed? [Y/n]

---

Committed: ghi9012
```

### Example 3: No Changes

```
> /tiki:commit

No changes to commit.
Working tree clean.
```

### Example 4: Interactive Staging

```
> /tiki:commit

## Checking Tiki State
Active: Issue #35 (Fix login redirect)
Phase: 1 of 1

## Unstaged Changes
 M src/routes/auth.ts    (target file)
 M src/config.ts         (unrelated)
 M debug.log             (should not commit)

Stage all? [Y/n/select]
> select

Enter files to stage (space-separated):
> src/routes/auth.ts

Staged: src/routes/auth.ts

## Proposed Commit
fix(auth): Fix login redirect after authentication (#35)

Phase 1 of 1: Fix login redirect
- Corrected redirect URL after successful login

Proceed? [Y/n]
```

## Integration with Execute

When `/tiki:execute` completes a phase:
1. It may prompt for a commit if there are uncommitted changes
2. The commit automatically includes phase context
3. State is updated to mark phase as committed

## Notes

- Always reference the issue number for traceability
- Phase info in commit body helps with git history analysis
- Commits during execution create a clear audit trail
- Use `--no-state` if you want to commit without updating Tiki tracking
- The commit skill reads state but only writes to git and optionally the plan file
