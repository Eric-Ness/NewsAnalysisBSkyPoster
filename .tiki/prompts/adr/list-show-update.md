# ADR List, Show, and Update Operations

## List ADRs

Display all ADRs in a table format:

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

Read all files in `.tiki/adr/` to build the table. Extract title, status, and date from each file's frontmatter/content.

## Show ADR

When showing a specific ADR:

1. Read `.tiki/adr/NNN-*.md` (match by number prefix)
2. Display the full content

```
## ADR-003: Use Prisma over TypeORM

**Status:** Accepted
**Date:** 2026-01-10

[Full ADR content displayed]

---
Update status: `/tiki:adr update 003 --status superseded`
```

## Update ADR

When updating an ADR:

```
/tiki:adr update 003 --status superseded --superseded-by 007
```

Update the ADR file:
- Change status
- Add superseded-by reference if applicable
- Update the date

Confirm the update:

```
Updated ADR-003:
- Status: Accepted -> Superseded
- Superseded by: ADR-007

View: `/tiki:adr show 003`
```

## ADR Status Values

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion, not yet decided |
| Accepted | Decision made and in effect |
| Deprecated | No longer recommended but still in use |
| Superseded | Replaced by another ADR |
| Rejected | Considered but not adopted |

## Integration with Issues

When an ADR relates to a specific issue or phase, include in Related section:

```markdown
## Related

- Issue #34: Add user authentication
- Phase 2: Database models implementation
- ADR-001: Use JWT for authentication (related decision)
```
