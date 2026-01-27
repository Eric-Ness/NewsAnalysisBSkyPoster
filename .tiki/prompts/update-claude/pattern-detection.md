# Pattern Detection

Gather patterns from multiple sources for CLAUDE.md synchronization.

## Source 1: Learned Patterns File

Read `.tiki/learned/patterns.json` if it exists:

```json
{
  "patterns": [
    {
      "type": "naming",
      "pattern": "Services use *Service.ts naming",
      "source": "observed in src/services/",
      "confidence": "high",
      "learnedAt": "2026-01-10T10:00:00Z"
    },
    {
      "type": "testing",
      "pattern": "Tests use describe/it blocks with given/when/then",
      "source": "observed in user.test.ts",
      "confidence": "high",
      "learnedAt": "2026-01-10T11:00:00Z"
    }
  ],
  "gotchas": [
    {
      "description": "Auth middleware must be applied before rate limiter",
      "source": "discovered during Issue #34",
      "severity": "medium"
    }
  ],
  "preferences": [
    {
      "preference": "Prefer early returns over nested conditionals",
      "source": "PR review feedback",
      "since": "2026-01-08"
    }
  ]
}
```

Filter for unsynced patterns (missing `syncedToClaude: true`).

## Source 2: Recent ADRs

Scan `.tiki/adr/` for architectural decisions:

```
Glob: .tiki/adr/*.md
```

Extract key decisions that should appear in CLAUDE.md:
- Database choices
- Framework selections
- API design decisions
- Authentication approaches

## Source 3: Execution History

Read completed plans in `.tiki/plans/` for patterns that emerged during implementation:
- Recurring file structures
- Common error handling patterns
- Integration approaches
- Testing strategies discovered

## Pattern Categories

| Category | Examples |
|----------|----------|
| naming | File naming, variable naming, function naming |
| structure | Folder organization, module structure |
| testing | Test patterns, coverage expectations |
| gotchas | Things to avoid, common mistakes |
| decisions | Architectural choices, library selections |
| preferences | Style preferences, code quality rules |
