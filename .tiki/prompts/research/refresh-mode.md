# Refresh Mode

Conditional prompt loaded when `--refresh` flag is present.

## Overview

When the `--refresh` flag is detected, existing research for the topic will be archived and new research conducted. This ensures fresh data while preserving historical research.

## Archive Existing Research

Before conducting new research, archive the existing document:

### Directory Structure

```
.tiki/research/{topic}/
  research.md           # Current research (will be replaced)
  archive/              # Historical research versions
    research-{YYYYMMDD}.md
```

### Archive Commands

```bash
# Create archive directory if needed
mkdir -p .tiki/research/{topic}/archive

# Move existing research to archive with timestamp
mv .tiki/research/{topic}/research.md .tiki/research/{topic}/archive/research-{timestamp}.md
```

The timestamp format is `YYYYMMDD` (e.g., `research-20260115.md`).

## User Messaging

Display these messages during refresh mode:

### Refresh Start Message

```
Refreshing research for "{topic}"...
Previous research from {date} will be archived.
```

Where `{date}` is the `researched_at` value from the existing document's frontmatter, formatted as a human-readable date.

### Archive Confirmation

```
Archived previous research to:
  .tiki/research/{topic}/archive/research-{timestamp}.md
```

## Refresh Workflow

1. **Display refresh message** - Notify user that refresh is in progress
2. **Create archive directory** - Ensure `.tiki/research/{topic}/archive/` exists
3. **Archive existing document** - Move `research.md` to archive with timestamp
4. **Confirm archive** - Display archive location to user
5. **Continue to research phase** - Proceed with Step 3 (Initialize Research Session)

## Notes

- The refresh flag bypasses the "Existing Research Found" prompt (Step 2e)
- Archived research is never deleted, allowing historical comparison
- The archive timestamp uses the current date, not the original research date
- After archiving, the research workflow continues normally with fresh agents
