# Staging Workflow

## Step 1: Check for Changes

```bash
git status --porcelain
```

If no changes staged or modified:
```
No changes to commit.

Use `git add <files>` to stage changes, or check `git status` for details.
```

## Step 2: Check Staged vs Unstaged

If there are already staged changes, show them:
```bash
git diff --cached --stat
```

If there are unstaged changes, present them:
```bash
git diff --stat
```

## Step 3: Present Options

Display to user:
```
Changes not staged:
  src/routes/auth.ts    | 45 +++++++++++++++
  src/middleware/jwt.ts | 12 ++++
  tests/auth.test.ts    | 30 ++++++++++

Stage all changes? [Y/n] or specify files:
```

## Step 4: Stage Based on Input

Stage based on user response:
```bash
git add .                    # If user confirms all
git add src/routes/auth.ts   # If user specifies files
```

## Selective Staging

When user wants to select files:
```
Enter files to stage (space-separated):
> src/routes/auth.ts src/middleware/jwt.ts

Staged: src/routes/auth.ts, src/middleware/jwt.ts
```

## Files to Avoid

Warn about committing:
- Log files (*.log, debug.log)
- Environment files (.env, .env.local)
- Build artifacts (dist/, node_modules/)
- Temporary files (*.tmp, .DS_Store)
