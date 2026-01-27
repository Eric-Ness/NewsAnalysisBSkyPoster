# Issue Creation Workflow

Handle creating GitHub issues from queue items, ADRs from triggers, and CLAUDE.md updates from conventions.

## Create GitHub Issue

For queue items (potential-issue, tech-debt, question, note):

```bash
gh issue create --title "<item title>" --body "## Background
Discovered during implementation of Issue #<source.issue>, Phase <source.phase>.

## Description
<item description>

## Suggested Priority
<item priority>

---
*Created from Tiki queue*" --label "<label1>" --label "<label2>"
```

After creation: `Created Issue #<number>: <title>`

## Convert Note to Issue

Same workflow as above. Transform note content into issue format.

## Create ADR from Trigger

1. **Find next ADR number:**
   ```bash
   ls .tiki/adr/*.md | sort -V | tail -1
   ```
   Start at 001 if none exist. Increment from highest.

2. **Generate ADR file** at `.tiki/adr/<NNN>-<kebab-case-title>.md`:

```markdown
# ADR-<NNN>: <trigger title>

## Status
Accepted

## Date
<current date YYYY-MM-DD>

## Context
During implementation of Issue #<issue> (Phase <phase>), this decision was made.
<trigger rationale>

## Decision
<trigger decision>

## Alternatives Considered
<For each alternative in trigger.details.alternatives, or:>
*No alternatives were formally documented during the decision.*

## Consequences
### Positive
- <inferred positive consequence>

### Negative
- <inferred negative consequence or trade-off>

## Related
- Issue #<issue>: <issue title>
- Phase <phase> of execution
```

3. Remove trigger from pending.json after success.

## Update CLAUDE.md from Convention

1. **Read/create CLAUDE.md** - Create minimal template if missing:
   ```markdown
   # CLAUDE.md
   Project-specific guidance for Claude Code.
   ## Code Conventions
   ```

2. **Map triggerType to section:**
   - `naming` -> `## Code Conventions` or `## Naming Conventions`
   - `structure` -> `## File Organization`
   - `pattern` -> `## Code Conventions`
   - `practice` -> `## Best Practices`

3. **Format entry:**
   ```markdown
   - <pattern description>
     - Rationale: <rationale>
     - Examples: `<example1>`, `<example2>`
     - Source: Issue #<issue>, Phase <phase>
   ```

4. Append to section, remove trigger from pending.json.
