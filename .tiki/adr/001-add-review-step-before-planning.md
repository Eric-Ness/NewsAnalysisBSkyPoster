# ADR-001: Add Review Step Before Planning Issues

## Status

Accepted

## Date

2026-01-14

## Context

The Tiki workflow for handling GitHub issues followed a direct path from fetching an issue to planning its implementation. In the YOLO automated workflow, this meant:

```
get-issue -> plan-issue -> audit-plan -> execute -> review-queue -> ship
```

However, this approach had a problem: Claude would sometimes plan issues that had fundamental problems - scope too large, missing dependencies, ambiguous requirements, or approaches that didn't fit the codebase. These problems would only surface during execution, wasting time and creating poor plans.

We needed a "think twice" mechanism that would catch these issues before committing to a plan.

## Decision

We will add a `/tiki:review-issue` command as a mandatory step before planning. This command:

1. Re-reads the GitHub issue with fresh eyes
2. Analyzes it for blocking concerns, warnings, and informational notes
3. Categorizes findings by severity (blocking, warning, info)
4. Posts findings as a GitHub comment for transparency
5. Returns a verdict (blocked, warnings, clean) that integrates with YOLO mode

The updated workflow becomes:

```
get-issue -> review-issue -> plan-issue -> audit-plan -> execute -> review-queue -> ship
```

## Alternatives Considered

### No Review Step (Status Quo)
- Pros: Faster workflow, less overhead
- Cons: Bad issues slip through, plans fail during execution, wasted effort

### Review Integrated into Plan Step
- Pros: Single command, no extra step
- Cons: Review concerns get lost in planning output, harder to separate concerns, can't pause YOLO when blocked

### Manual Review Only
- Pros: Human judgment before any automation
- Cons: Defeats the purpose of automation, bottleneck on human availability

### AI Review Without Severity Levels
- Pros: Simpler implementation
- Cons: Can't differentiate "must fix" from "nice to know", YOLO can't make intelligent decisions about whether to continue

## Consequences

### Positive
- Catches scope problems before wasting time on bad plans
- Surfaces missing dependencies and blockers early
- Creates a record of pre-planning analysis on the GitHub issue
- YOLO mode can intelligently pause on blocking concerns
- Encourages better issue writing by surfacing ambiguities
- Severity levels allow nuanced handling (block vs warn vs inform)

### Negative
- Adds an extra step to the workflow
- Increases token usage for each issue processed
- May occasionally flag false positives as "blocking"
- Requires maintaining another command file

### Neutral
- Review comments on GitHub issues may become noisy if overused
- Teams need to understand the blocking/warning/info distinction
- `--force-review` flag provides escape hatch for override

## Related

- [review-issue.md](.claude/commands/tiki/review-issue.md): The command implementation
- [yolo.md](.claude/commands/tiki/yolo.md): YOLO workflow integration
- [plan-review-issue.md](Notes/plan-review-issue.md): Original planning document for blocking concern handling
