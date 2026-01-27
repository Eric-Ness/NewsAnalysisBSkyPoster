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

### Step 2: Execute Mode

**Create new ADR:**
Read `.tiki/prompts/adr/create-workflow.md` and follow the creation steps including context gathering, drafting, and file writing.

**List/Show/Update ADRs:**
Read `.tiki/prompts/adr/list-show-update.md` and follow the display or update steps.

### Step 3: Auto-Generation (During Execution)

When making significant decisions during issue execution, read `.tiki/prompts/adr/auto-generation.md` for the auto-ADR workflow and trigger conditions.

## Notes

- ADRs are stored in `.tiki/adr/` by default
- The directory can be configured in `.tiki/config.json`
- ADRs are immutable once accepted - create a new one to change decisions
- Use superseded status to link old decisions to new ones
- Keep ADRs concise - they're for recording decisions, not documentation
