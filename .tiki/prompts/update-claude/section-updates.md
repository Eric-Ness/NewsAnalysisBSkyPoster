# Section Updates

Logic for categorizing discoveries and applying changes to CLAUDE.md.

## Categorize Discoveries

Organize gathered patterns into sections:

```
## Patterns to Add

### Code Conventions
- [ ] Services use *Service.ts naming
- [ ] Repositories use *Repository.ts naming
- [ ] DTOs in src/dto/ folder

### Testing Patterns
- [ ] Use given/when/then comments
- [ ] Mock external services with MSW
- [ ] E2E tests use page objects

### Gotchas
- [ ] Auth middleware must come before rate limiter
- [ ] Prisma client needs regeneration after schema changes

### Team Preferences
- [ ] Prefer early returns
- [ ] Use named exports over default exports
```

## Preview Format

Present changes before applying:

```
## CLAUDE.md Update Preview

The following will be added to CLAUDE.md:

### New Sections

**Code Conventions** (new section)
- Services use *Service.ts naming convention

**Testing Patterns** (appending to existing)
- Use given/when/then comments in test descriptions

**Gotchas** (appending to existing)
- Auth middleware must be applied before rate limiter

### From Recent Decisions

**ADR-003**: Use Prisma over TypeORM
> Adding: "Database access uses Prisma ORM"

---
Apply these changes? [Yes/No/Edit]
```

## Apply Changes

### If CLAUDE.md Doesn't Exist

Create new file with template:

```markdown
# CLAUDE.md

> Project context for Claude. Auto-generated and maintained by Tiki.
> Last updated: [DATE]

## Project Overview

[To be filled in manually or by /map-codebase]

## Code Conventions

[Discovered conventions]

## Testing

[Testing patterns]

## Gotchas

[Gotchas discovered]

## Key Decisions

[ADR-sourced decisions]

## File Locations

[Directory conventions]
```

### If CLAUDE.md Exists

Use Edit tool to:
1. Append to existing sections
2. Create new sections if category doesn't exist
3. Preserve existing content and structure

Report changes made:

```
Updating CLAUDE.md...

Added to "Code Conventions":
- Services use *Service.ts naming convention

Added to "Gotchas":
- Auth middleware must be applied before rate limiter

Created new section "Key Decisions":
- Database: Prisma ORM (ADR-003)

CLAUDE.md updated successfully.
```

## Mark Patterns Synced

After applying changes, update `.tiki/learned/patterns.json`:

```json
{
  "patterns": [
    {
      "type": "naming",
      "pattern": "Services use *Service.ts naming",
      "syncedToClaude": true,
      "syncedAt": "2026-01-10T14:00:00Z"
    }
  ]
}
```

Add `syncedToClaude: true` and `syncedAt` timestamp to each applied pattern.
