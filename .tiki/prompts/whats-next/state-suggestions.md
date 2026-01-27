# State-Specific Output Templates

Output structure reference for whats-next by state type.

## Core States

### In Progress

- **Currently Active**: Issue #, title, phase X of Y, status, last activity
- **Suggested**: `/tiki:execute N`
- Include: Also Pending (other plans, queue count)

### Paused

- **Paused Work**: Issue #, paused at phase, time ago, reason
- **Suggested**: `/tiki:resume N` or `/tiki:execute N --from X`

### Failed

- **Failed Execution**: Issue #, phase that failed, error summary
- **Suggested Actions** (numbered):
  1. `/tiki:heal N`
  2. `/tiki:execute N --from X`
  3. `/tiki:skip-phase X`

### Plans Ready

- **Ready to Execute**: Table (Issue | Title | Phases | Priority)
- **Suggested**: `/tiki:execute N` (highest priority)

### Queue Pending

- **Queue Items (N)**: Count by type (issues, questions)
- **Suggested**: `/tiki:review-queue`

### Nothing Active

- **Current State**: No active work, no planned issues
- **Suggested**: `gh issue list`, `/tiki:get-issue`, `/tiki:plan-issue`

## Release Context

Add release section when issue is part of active release:

### In Release (active work)

- **Release Context**: Release name, X of Y completed (%)
- Table: Issue | Title | Status (bold current)

### Next Issue Ready

- **Active Release**: Name, progress
- **Next in Release**: Issue #, status, phases, dependencies, requirements
- **Remaining**: List other issues

### Just Completed

- **Just Completed**: Issue # - completed!
- **Release Progress**: Name, count (+1 since last)
- **Requirements Progress**: List with status
- **Next in Release**: Next issue details
- **Suggested**: `/tiki:execute N` or `/tiki:release-status`

### Nearly Complete

- **Active Release - Final Issue!**: Name, 80%+ progress
- **Final Issue**: Issue #, status, note this is last
- **Suggested**: `/tiki:plan-issue N`, then `/tiki:release-ship`

## Combined Output

When multiple states present, show sections in priority order:

1. Currently Active / Paused / Failed
2. Release Context (if applicable)
3. Queue (if items pending)
4. Also Planned (other ready work)
5. Suggested Action (primary recommendation)
