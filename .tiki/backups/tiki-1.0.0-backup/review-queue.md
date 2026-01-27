---
type: prompt
name: tiki:review-queue
description: Review and process items discovered during execution. Use when there are queue items to review, create issues from, or dismiss.
allowed-tools: Read, Write, Bash, Glob
argument-hint: [--create-all] [--dismiss-all] [--approve-all-docs] [--dismiss-all-adr] [--dismiss-all-claude] [--issues] [--docs] [--adr] [--claude]
---

# Review Queue

Review items from phase execution - potential issues, questions, notes, and documentation triggers.

## Usage

- `/tiki:review-queue` - Review all items interactively
- `--issues` - Queue items only | `--docs` - Triggers only
- `--adr` - ADR triggers only | `--claude` - Convention triggers only
- `--create-all` - Create issues + high-confidence ADRs
- `--dismiss-all` - Clear all | `--approve-all-docs` - Process all triggers
- `--dismiss-all-adr` / `--dismiss-all-claude` - Dismiss specific trigger types

## Instructions

### Step 1: Load Queue and Triggers

Read `.tiki/queue/pending.json`:
- Fields: `items[]` with id, type, title, description, source{issue, phase}, priority, labels, createdAt

Read `.tiki/triggers/pending.json` (create empty `{triggers:[]}` if missing):
- Fields: `triggers[]` with id, triggerType (adr|convention), title, decision/pattern, rationale, confidence, source, createdAt

**Empty state:** If both empty, show "No items or triggers pending. Use `/tiki:state` for status."

### Step 2: Apply Filters

Parse filter flags:
- `--issues`: Queue items only
- `--docs`: All triggers only
- `--adr`: ADR triggers only
- `--claude`: Convention triggers only
- No filter: Show all

### Step 3: Display Items

Group and display filtered items:

```
## Queue Review

**{count} items** pending review

### Potential Issues ({count})
#### 1. <title>
- **Source:** Issue #<n>, Phase <n>
- **Priority:** <priority>
- **Description:** <description>
**Actions:** [Create Issue] [Dismiss] [Edit]

### Questions ({count})
**Actions:** [Answer] [Convert to Issue] [Dismiss]

### Notes ({count})
**Actions:** [Convert to Issue] [Add to .tiki/CONCERNS.md] [Dismiss]

### ADR Triggers ({count})
- **Confidence:** high|medium|low
**Actions:** [Create ADR] [View] [Edit] [Dismiss]

### Convention Triggers ({count})
- **Pattern:** <pattern>
**Actions:** [Update CLAUDE.md] [View] [Edit] [Dismiss]
```

### Step 4: Process Items

**Batch operations:** If batch flag provided, load `.tiki/prompts/review-queue/batch-operations.md` and execute.

**Interactive processing:** Handle user action selection:

- **Dismiss:** Remove from queue, add to `processed[]`
- **Answer Question:** Get response, offer: create issue, add to CLAUDE.md, or dismiss

**Issue/ADR/CLAUDE.md creation:** Load `.tiki/prompts/review-queue/create-issue.md` for:
- [Create Issue] or [Convert to Issue]
- [Create ADR]
- [Update CLAUDE.md]

**View/Edit triggers:** Display full details, allow modification before processing.

### Step 5: Update Files

After each action, update `.tiki/queue/pending.json` and `.tiki/triggers/pending.json`:
- Remove processed items from `items[]`/`triggers[]`
- Add to `processed[]` with: id, action, timestamp, (issueNumber|adrPath if created)

### Step 6: Summary

```
## Queue Processing Complete

**Processed {count} items and triggers:**
- {n} issues created (#{n1}, #{n2})
- {n} ADRs created
- {n} conventions added to CLAUDE.md
- {n} items dismissed

**Remaining:** {count} items, {count} triggers
```

## Queue Item Types

| Type | Description | Actions |
|------|-------------|---------|
| `potential-issue` | Work to track | Create issue, Dismiss |
| `question` | Needs input | Answer, Convert, Dismiss |
| `note` | Observation | Add to docs, Convert, Dismiss |
| `blocker` | Blocking issue | Investigate, Create issue |
| `tech-debt` | Code quality | Create issue, Add to CONCERNS.md |
