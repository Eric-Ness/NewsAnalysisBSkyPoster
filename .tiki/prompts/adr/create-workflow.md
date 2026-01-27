# ADR Create Workflow

## Step 1: Get Next Number

Read `.tiki/adr/` directory to find the next number:

```bash
ls .tiki/adr/*.md | sort -V | tail -1
```

If no ADRs exist, start at 001.

## Step 2: Gather Context

Ask the user for details if not provided:

```
## New ADR: {Title}

I'll help you document this decision. Please provide:

1. **Context**: What problem or situation prompted this decision?
2. **Decision**: What was decided? (I have the title, but any details?)
3. **Alternatives**: What other options were considered?
4. **Consequences**: What are the implications of this choice?
```

Or if context is clear from recent work, propose the content:

```
Based on our recent implementation, I'll draft this ADR:

## ADR-{NNN}: {Title}

**Context**: {Describe the problem/situation}

**Decision**: {What was decided}

**Alternatives Considered**:
- Option A: {pros/cons}
- Option B: {pros/cons}

**Consequences**:
- (+) {Positive consequence}
- (-) {Negative consequence}

Does this look right? [Edit/Accept]
```

## Step 3: Write the ADR File

Create `.tiki/adr/NNN-kebab-case-title.md`:

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

## Step 4: Confirm Creation

```
Created: .tiki/adr/{NNN}-{kebab-case-title}.md

ADR-{NNN} has been recorded.

View with: `/tiki:adr show {NNN}`
List all: `/tiki:adr list`
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
