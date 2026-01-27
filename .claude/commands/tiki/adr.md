---
type: prompt
name: tiki:adr
description: Create and manage Architecture Decision Records. Use when documenting significant technical decisions, library choices, or architectural patterns.
allowed-tools: Read, Write, Edit, Glob, Grep
argument-hint: ["title"] | list | show <number> | update <number>
---

# ADR (Architecture Decision Record)

Create and manage Architecture Decision Records for documenting significant technical decisions.

## Usage

```
/tiki:adr "Use Prisma over TypeORM"
/tiki:adr list
/tiki:adr show 001
/tiki:adr update 001 --status superseded
```

## Instructions

### Step 1: Determine Mode

Parse the command to determine what action to take:

| Command | Action |
|---------|--------|
| `/tiki:adr "title"` | Create new ADR |
| `/tiki:adr list` | List all ADRs |
| `/tiki:adr show NNN` | Display specific ADR |
| `/tiki:adr update NNN` | Modify an existing ADR |
| `/tiki:adr` (no args) | Interactive mode - ask what to do |

### Step 2: Create New ADR

When creating a new ADR:

#### 2a. Get Next Number

Read `.tiki/adr/` directory to find the next number:

```bash
# Find highest numbered ADR
ls .tiki/adr/*.md | sort -V | tail -1
```

If no ADRs exist, start at 001.

#### 2b. Gather Context

Ask the user for details if not provided:

```
## New ADR: Use Prisma over TypeORM

I'll help you document this decision. Please provide:

1. **Context**: What problem or situation prompted this decision?
2. **Decision**: What was decided? (I have the title, but any details?)
3. **Alternatives**: What other options were considered?
4. **Consequences**: What are the implications of this choice?
```

Or if the context is clear from recent work, propose the content:

```
Based on our recent implementation, I'll draft this ADR:

## ADR-003: Use Prisma over TypeORM

**Context**: We needed an ORM for the new authentication system.
During Phase 2 of Issue #34, we evaluated options.

**Decision**: Use Prisma for database access.

**Alternatives Considered**:
- TypeORM: More mature but verbose, complex migrations
- Knex: Lower level, would need more boilerplate
- Raw SQL: Maximum control but no type safety

**Consequences**:
- (+) Strong TypeScript integration
- (+) Auto-generated types from schema
- (+) Intuitive migration system
- (-) Less flexible for complex queries
- (-) Team needs to learn Prisma syntax

Does this look right? [Edit/Accept]
```

#### 2c. Write the ADR File

Create `.tiki/adr/NNN-kebab-case-title.md`:

```markdown
# ADR-003: Use Prisma over TypeORM

## Status

Accepted

## Date

2026-01-10

## Context

We needed an ORM for the new authentication system. The project uses TypeScript
throughout, so type safety was a priority. During Phase 2 of Issue #34, we
evaluated several options.

## Decision

We will use Prisma as our ORM for all database operations.

## Alternatives Considered

### TypeORM
- Pros: Mature ecosystem, decorator-based models
- Cons: Verbose configuration, complex migration system, weaker TypeScript inference

### Knex
- Pros: Flexible query builder, lightweight
- Cons: No ORM features, requires manual type definitions

### Raw SQL
- Pros: Maximum control, no abstraction overhead
- Cons: No type safety, manual query building, security risks

## Consequences

### Positive
- Strong TypeScript integration with auto-generated types
- Intuitive schema definition with Prisma Schema
- Built-in migration system that tracks changes
- Excellent developer experience with Prisma Studio

### Negative
- Less flexibility for highly complex queries (may need raw SQL escape hatch)
- Team needs to learn Prisma-specific syntax
- Prisma Client needs regeneration after schema changes

### Neutral
- Adds prisma dependency to project
- Requires PostgreSQL-compatible database (or adjust for others)

## Related

- Issue #34: Add user authentication
- Phase 2: Database models implementation
```

#### 2d. Confirm Creation

```
Created: .tiki/adr/003-use-prisma-over-typeorm.md

ADR-003 has been recorded.

View with: `/tiki:adr show 003`
List all: `/tiki:adr list`
```

### Step 3: List ADRs

When listing ADRs:

```
## Architecture Decision Records

| # | Title | Status | Date |
|---|-------|--------|------|
| 001 | Use JWT for authentication | Accepted | 2026-01-08 |
| 002 | Adopt hexagonal architecture | Accepted | 2026-01-09 |
| 003 | Use Prisma over TypeORM | Accepted | 2026-01-10 |
| 004 | API versioning strategy | Proposed | 2026-01-10 |

---
View details: `/tiki:adr show <number>`
Create new: `/tiki:adr "Decision title"`
```

### Step 4: Show ADR

When showing a specific ADR:

1. Read `.tiki/adr/NNN-*.md`
2. Display the full content

```
## ADR-003: Use Prisma over TypeORM

**Status:** Accepted
**Date:** 2026-01-10

[Full ADR content displayed]

---
Update status: `/tiki:adr update 003 --status superseded`
```

### Step 5: Update ADR

When updating an ADR:

```
/tiki:adr update 003 --status superseded --superseded-by 007
```

Update the ADR file:
- Change status
- Add superseded-by reference if applicable
- Update the date

```
Updated ADR-003:
- Status: Accepted → Superseded
- Superseded by: ADR-007

View: `/adr show 003`
```

## ADR Status Values

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion, not yet decided |
| Accepted | Decision made and in effect |
| Deprecated | No longer recommended but still in use |
| Superseded | Replaced by another ADR |
| Rejected | Considered but not adopted |

## Auto-Generation

During execution, when Claude makes significant decisions, it should auto-generate ADRs.

Trigger conditions:
- Choosing between libraries/frameworks
- Selecting architectural patterns
- Making security-related choices
- Deciding on data modeling approaches
- Picking testing strategies

Example auto-generation:

```
I chose to implement the repository pattern for data access.

Auto-generating ADR...

Created: .tiki/adr/004-use-repository-pattern.md

This decision has been recorded for future reference.
Continuing with implementation...
```

## ADR Template

```markdown
# ADR-{NUMBER}: {Title}

## Status

{Proposed | Accepted | Deprecated | Superseded | Rejected}

## Date

{YYYY-MM-DD}

## Context

{What is the issue that we're seeing that is motivating this decision?}

## Decision

{What is the change that we're proposing and/or doing?}

## Alternatives Considered

### {Alternative 1}
- Pros: ...
- Cons: ...

### {Alternative 2}
- Pros: ...
- Cons: ...

## Consequences

### Positive
- {Positive consequence 1}
- {Positive consequence 2}

### Negative
- {Negative consequence 1}

### Neutral
- {Neutral consequence}

## Related

- {Links to issues, other ADRs, documentation}
```

## File Naming Convention

ADR files follow this pattern:
```
.tiki/adr/NNN-kebab-case-title.md
```

Examples:
- `001-use-jwt-for-authentication.md`
- `002-adopt-hexagonal-architecture.md`
- `003-use-prisma-over-typeorm.md`

## Integration with Issues

When an ADR relates to a specific issue or phase:

```markdown
## Related

- Issue #34: Add user authentication
- Phase 2: Database models implementation
- ADR-001: Use JWT for authentication (related decision)
```

## Notes

- ADRs are stored in `.tiki/adr/` by default
- The directory can be configured in `.tiki/config.json`
- ADRs are immutable once accepted - create a new one to change decisions
- Use superseded status to link old decisions to new ones
- Keep ADRs concise - they're for recording decisions, not documentation
- Include enough context that future developers understand the "why"
