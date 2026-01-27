# Commit Examples

## Example 1: Mid-Phase Commit

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

## Example 2: No Active Issue

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

## Example 3: No Changes

```
> /tiki:commit

No changes to commit.
Working tree clean.
```

## Example 4: Interactive Staging

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

## HEREDOC Commit Format

Always use HEREDOC for multi-line commit messages:
```bash
git commit -m "$(cat <<'EOF'
feat(auth): Add login endpoint (#34)

Phase 2 of 3: Add login endpoint
- Implemented POST /api/login
- Added JWT token generation
EOF
)"
```
