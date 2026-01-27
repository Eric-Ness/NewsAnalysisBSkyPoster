# Commit Message Format

## With Active Tiki Issue

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

## Without Active Tiki Issue

If no Tiki state exists, create a standard commit:

```
<type>(<scope>): <description>

<optional body>
```

## Type Selection

| Type | When to Use |
|------|-------------|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug or issue |
| `refactor` | Restructuring code without changing behavior |
| `test` | Adding or updating tests |
| `docs` | Documentation changes |
| `chore` | Build, config, dependency updates |
| `style` | Formatting, whitespace (no code change) |

## Scope Selection

Use the area of the codebase being changed:
- `auth`, `api`, `db`, `ui`, `config`, `tests`, etc.

## Description Guidelines

- Start with lowercase verb (add, fix, update, remove)
- Keep under 50 characters
- Don't end with period

## State Update Format

After commit, update the plan file `.tiki/plans/issue-N.json` with commit info:

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
