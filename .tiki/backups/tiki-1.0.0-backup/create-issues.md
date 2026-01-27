---
type: prompt
name: tiki:create-issues
description: Batch create GitHub issues from queue items or code assessment findings. Use when you want to create multiple issues from discovered items or assessment reports.
allowed-tools: Read, Bash, Glob, Grep
argument-hint: [--from-queue] [--from-assessment] [--labels] [--priority <level>] [--dry-run]
---

# Create Issues

Batch-creates GitHub issues from the Tiki queue or from a code quality assessment report.

## Usage

```
/tiki:create-issues                        # Interactive - shows sources and prompts
/tiki:create-issues --from-queue           # Create from pending queue items
/tiki:create-issues --from-assessment      # Create from CODE_QUALITY_ASSESSMENT.md
/tiki:create-issues --dry-run              # Preview without creating
/tiki:create-issues --labels --priority high  # With auto-labels and priority
```

## Instructions

### Step 1: Determine Source

**If `--from-queue` or no arguments:** Read `.tiki/queue/pending.json` for items with `type: "potential-issue"`.

**If `--from-assessment`:** Read `.tiki/prompts/create-issues/from-assessment.md` for parsing guidance, then parse `docs/CODE_QUALITY_ASSESSMENT.md`.

### Step 2: Display Preview

Show issues to be created with title, priority, labels, and source. If `--dry-run`, stop after preview.

### Step 3: Create Issues

Use `gh issue create` for each item:

```bash
gh issue create \
  --title "Issue title" \
  --body "$(cat <<'EOF'
## Description
[Item description]

## Source
[Queue item ID or assessment section]

---
*Created via Tiki /tiki:create-issues*
EOF
)" \
  --label "label1" \
  --label "label2"
```

### Step 4: Apply Labels

When `--labels` specified, auto-apply based on category:

| Category | Labels |
|----------|--------|
| Security | `security` |
| Testing | `testing`, `tech-debt` |
| Architecture | `architecture`, `refactor` |
| Documentation | `documentation` |
| Error Handling | `bug`, `reliability` |
| Dependencies | `dependencies`, `maintenance` |
| Code Quality | `tech-debt`, `cleanup` |

### Step 5: Apply Priority

When `--priority` specified, add priority labels:

| Priority | Labels |
|----------|--------|
| `critical` | `critical`, `P0` |
| `high` | `high-priority`, `P1` |
| `medium` | `medium-priority`, `P2` |
| `low` | `low-priority`, `P3` |

### Step 6: Update Queue

If source was queue, update `.tiki/queue/pending.json`:

- Move processed items from `items` to `processed` array
- Record `issueNumber` and `processedAt` timestamp

### Step 7: Display Summary

Show table of created issues with number, title, labels, and priority. Include queue status and next steps.

## Options Reference

| Option | Description |
|--------|-------------|
| `--from-queue` | Create issues from `.tiki/queue/pending.json` |
| `--from-assessment` | Create issues from `docs/CODE_QUALITY_ASSESSMENT.md` |
| `--labels` | Auto-apply labels based on category |
| `--priority <level>` | Set priority: `critical`, `high`, `medium`, `low` |
| `--dry-run` | Preview issues without creating them |

## Notes

- Issues include source tracking (queue item ID or assessment section)
- Queue is updated after successful creation (items moved to `processed`)
- Use `--dry-run` to preview before creating
- Requires authenticated `gh` CLI (`gh auth status`)
