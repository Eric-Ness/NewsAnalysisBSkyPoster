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

```bash
/tiki:update-claude                  # Auto-detect and sync patterns
/tiki:update-claude --from-learned   # Only sync from learned patterns file
/tiki:update-claude --interactive    # Walk through categories step-by-step
/tiki:update-claude --dry-run        # Preview changes without applying
```

## Instructions

### Step 1: Parse Arguments

Extract flags from arguments:

- **--from-learned**: Only use `.tiki/learned/patterns.json` as source
- **--interactive**: Enable step-by-step guided mode
- **--dry-run**: Show preview without applying changes

### Step 2: Gather Patterns

Read `.tiki/prompts/update-claude/pattern-detection.md` and follow its instructions to gather patterns from:

- Learned patterns file
- Recent ADRs
- Execution history

### Step 3: Read Existing CLAUDE.md

If `CLAUDE.md` exists, read it to:

- Understand current structure
- Avoid duplicate entries
- Identify sections for appending

### Step 4: Handle Interactive Mode

If `--interactive` flag is present:
Read `.tiki/prompts/update-claude/interactive-mode.md` and follow the step-by-step workflow for each category.

### Step 5: Apply Updates

Read `.tiki/prompts/update-claude/section-updates.md` and follow instructions to:

1. Categorize discovered patterns
2. Present preview of changes
3. If `--dry-run`: Show preview and stop
4. Otherwise: Apply changes and mark patterns as synced

### Step 6: Completion

Show summary:

```text
## CLAUDE.md Updated

**Changes made:**
- Added X code conventions
- Added Y gotchas
- Synced Z learned patterns

**Next steps:**
- View changes: `cat CLAUDE.md`
- Add more patterns: `/tiki:update-claude --interactive`
```

## Notes

- CLAUDE.md is Claude's primary context file - keep it concise
- Only sync high-confidence patterns
- Use `--dry-run` to preview before applying
