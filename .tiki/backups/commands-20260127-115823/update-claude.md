---
type: prompt
name: tiki:update-claude
description: Update CLAUDE.md from patterns learned during implementation. Use to sync discovered conventions and project knowledge.
allowed-tools: Read, Write, Edit, Glob, Grep
argument-hint: [--from-learned] [--interactive] [--dry-run]
---

# Update Claude

Updates CLAUDE.md (or creates one) based on patterns learned during implementation.

## Usage

```
/tiki:update-claude
/tiki:update-claude --from-learned
/tiki:update-claude --interactive
/tiki:update-claude --dry-run
```

## Instructions

### Step 1: Gather Learned Patterns

Check multiple sources for patterns to add:

#### Source 1: Learned Patterns File

Read `.tiki/learned/patterns.json`:

```json
{
  "patterns": [
    {
      "type": "naming",
      "pattern": "Services use *Service.ts naming",
      "source": "observed in src/services/",
      "confidence": "high",
      "learnedAt": "2026-01-10T10:00:00Z"
    },
    {
      "type": "testing",
      "pattern": "Tests use describe/it blocks with given/when/then",
      "source": "observed in user.test.ts",
      "confidence": "high",
      "learnedAt": "2026-01-10T11:00:00Z"
    }
  ],
  "gotchas": [
    {
      "description": "Auth middleware must be applied before rate limiter",
      "source": "discovered during Issue #34",
      "severity": "medium"
    }
  ],
  "preferences": [
    {
      "preference": "Prefer early returns over nested conditionals",
      "source": "PR review feedback",
      "since": "2026-01-08"
    }
  ]
}
```

#### Source 2: Recent ADRs

Scan `.tiki/adr/` for recent decisions:

```
Glob: .tiki/adr/*.md
```

Extract key decisions that should be in CLAUDE.md.

#### Source 3: Execution History

Read completed plans in `.tiki/plans/` for patterns that emerged.

### Step 2: Read Existing CLAUDE.md

If CLAUDE.md exists, read it to avoid duplicates:

```
Read: CLAUDE.md
```

Parse existing sections to understand current structure.

### Step 3: Categorize New Information

Organize discoveries into categories:

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

### Step 4: Present Changes

Show the user what will be added:

```
## CLAUDE.md Update Preview

The following will be added to CLAUDE.md:

### New Sections

**Code Conventions** (new section)
- Services use *Service.ts naming convention
- Repositories use *Repository.ts naming convention
- DTOs are stored in src/dto/ folder

**Testing Patterns** (appending to existing)
- Use given/when/then comments in test descriptions
- Mock external services with MSW

**Gotchas** (appending to existing)
- Auth middleware must be applied before rate limiter
- Prisma client needs regeneration after schema changes

### From Recent Decisions

**ADR-003**: Use Prisma over TypeORM
→ Adding: "Database access uses Prisma ORM"

---
Apply these changes? [Yes/No/Edit]
```

### Step 5: Apply Changes

#### If CLAUDE.md doesn't exist, create it:

```markdown
# CLAUDE.md

> Project context for Claude. Auto-generated and maintained by Tiki.
> Last updated: 2026-01-10

## Project Overview

[To be filled in manually or by /map-codebase]

## Code Conventions

- Services use `*Service.ts` naming convention
- Repositories use `*Repository.ts` naming convention
- DTOs are stored in `src/dto/` folder
- Prefer early returns over nested conditionals
- Use named exports over default exports

## Testing

- Tests use describe/it blocks with given/when/then comments
- Mock external services with MSW
- E2E tests use the page object pattern

## Gotchas

- Auth middleware must be applied before rate limiter
- Prisma client needs regeneration after schema changes
- Don't use `any` type - use `unknown` and narrow

## Key Decisions

- **Database**: Prisma ORM (ADR-003)
- **Auth**: JWT with refresh tokens (ADR-001)
- **API Style**: REST with OpenAPI docs

## File Locations

- Services: `src/services/`
- API routes: `src/api/`
- Types: `src/types/`
- Tests: Next to source files (`*.test.ts`)
```

#### If CLAUDE.md exists, update specific sections:

Use Edit tool to append to relevant sections or create new sections.

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

### Step 6: Update Learned File

Mark patterns as synced:

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

### Step 7: Confirm Completion

```
## CLAUDE.md Updated

**Changes made:**
- Added 3 code conventions
- Added 2 gotchas
- Created Key Decisions section
- Synced 5 learned patterns

**Next time Claude reads CLAUDE.md, it will know:**
- How to name service files
- Testing patterns to follow
- Gotchas to avoid

---
View changes: `cat CLAUDE.md`
Add more patterns: `/tiki:update-claude --interactive`
```

## Interactive Mode

With `--interactive`:

```
## Update CLAUDE.md - Interactive Mode

I'll walk you through adding patterns to CLAUDE.md.

### Step 1: Code Conventions

What naming conventions does this project use?

Examples:
- "Components are PascalCase"
- "Files are kebab-case"
- "Services end with Service.ts"

Your input (or 'skip'):
```

Continue through categories:
1. Code Conventions
2. File Organization
3. Testing Patterns
4. Common Gotchas
5. Key Decisions
6. Team Preferences

### Dry Run Mode

With `--dry-run`:

```
## CLAUDE.md Update Preview (Dry Run)

Would add the following to CLAUDE.md:

### Code Conventions (append)
+ Services use *Service.ts naming convention
+ Repositories use *Repository.ts naming convention

### Gotchas (append)
+ Auth middleware must be applied before rate limiter

No changes made. Run without --dry-run to apply.
```

## Learning New Patterns

During normal development, patterns can be learned by:

### Explicit Learning

When the user says "remember this" or "note this pattern":

```
User: "Remember that we always use Zod for validation"

Claude: Noted. Adding to learned patterns:
- Validation: Use Zod for all schema validation

This will be synced to CLAUDE.md with `/tiki:update-claude`
```

Write to `.tiki/learned/patterns.json`.

### Implicit Learning

During execution, when Claude observes consistent patterns:

```
Observing pattern in codebase:
- 15 service files all use *Service.ts naming
- Confidence: High

Adding to learned patterns for review.
```

## Pattern Categories

| Category | Examples |
|----------|----------|
| naming | File naming, variable naming, function naming |
| structure | Folder organization, module structure |
| testing | Test patterns, coverage expectations |
| gotchas | Things to avoid, common mistakes |
| decisions | Architectural choices, library selections |
| preferences | Style preferences, code quality rules |

## Notes

- CLAUDE.md is the primary context file Claude reads each session
- Keep it concise - too much info reduces effectiveness
- Patterns should be high-confidence before adding
- Use `/tiki:update-claude --dry-run` to preview changes
- Learned patterns file can be reviewed before syncing
- Integration with `/tiki:map-codebase` for initial population
