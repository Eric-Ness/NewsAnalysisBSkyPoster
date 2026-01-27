# Batch Operations

Process multiple queue items and triggers with a single command.

## --create-all

Create GitHub issues for queue items AND ADRs for high-confidence triggers:

**What gets processed:**
- Queue items: `potential-issue`, `tech-debt` -> GitHub Issues
- ADR triggers: `confidence: high` -> ADRs created
- Skipped: low/medium confidence ADRs, convention triggers

```
Processing {count} queue items and {count} high-confidence ADR triggers...

Issues Created:
  Created #{n}: <title>

ADRs Created:
  Created .tiki/adr/<NNN>-<title>.md

Summary:
  {n} issues created
  {n} ADRs created from high-confidence triggers
  {n} ADR triggers skipped (low/medium confidence)
  {n} convention triggers skipped
```

## --dismiss-all

Clear all queue items and all triggers without action:

```
Dismissing {count} queue items and {count} triggers...

Dismissed:
  {n} queue items removed
  {n} ADR triggers removed
  {n} convention triggers removed

All items and triggers cleared.
```

## --approve-all-docs

Process ALL documentation triggers (regardless of confidence):

```
Processing all documentation triggers...

ADRs Created:
  Created .tiki/adr/<NNN>-<title>.md

CLAUDE.md Updates:
  Added: <convention title>

Summary:
  {n} ADRs created
  {n} conventions added to CLAUDE.md
```

## --dismiss-all-adr

Dismiss only ADR triggers:

```
Dismissing all ADR triggers...

Dismissed:
  - <trigger title>

{n} ADR triggers dismissed.
Queue items and convention triggers unchanged.
```

## --dismiss-all-claude

Dismiss only convention triggers:

```
Dismissing all convention triggers...

Dismissed:
  - <trigger title>

{n} convention triggers dismissed.
Queue items and ADR triggers unchanged.
```

## Update Files After Batch

Update both files after processing:

**`.tiki/queue/pending.json`**: Remove processed items, add to `processed[]` array.

**`.tiki/triggers/pending.json`**: Remove processed triggers, add to `processed[]` array with action and timestamp.
