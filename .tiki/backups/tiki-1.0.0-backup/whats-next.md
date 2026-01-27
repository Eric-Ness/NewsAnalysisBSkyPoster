---
type: prompt
name: tiki:whats-next
description: Show current status and suggest next actions. Use when resuming work, checking progress, or deciding what to do next.
allowed-tools: Read, Glob, Bash
---

# What's Next

Display current Tiki state and provide actionable suggestions for what to do next.

## Usage

```
/tiki:whats-next
```

## Instructions

### Step 1: Gather State Information

Read all relevant state files:

- `.tiki/state/current.json` - Active execution state
- `.tiki/plans/issue-*.json` - All plans
- `.tiki/queue/pending.json` - Queue items
- `.tiki/context/*.json` - Saved context
- `.tiki/releases/*.json` - Active releases (excluding archive/)

### Step 2: Determine Current Situation

| Situation | Indicators |
|-----------|------------|
| Active execution | `current.json` has `status: "in_progress"` |
| Paused work | `current.json` has `pausedAt` set |
| Failed phase | Plan has phase with `status: "failed"` |
| Planned but not started | Plans exist with `status: "planned"` |
| Active release with next issue | Release has issues with status != "completed" |
| Queue needs review | `pending.json` has items |
| Nothing in progress | No active state, no pending plans |

**Release context check:** When releases exist, check if current issue is in a release, find next ready issue (status "not_planned" or "planned" with satisfied dependencies), and calculate release progress (completed/in_progress/remaining counts).

### Step 3: Build Recommendations

Based on situation, provide specific actionable suggestions. Include release context when applicable. For just-completed release issues, suggest the next release issue.

## Output Format

Read `.tiki/prompts/whats-next/state-suggestions.md` for state-specific output templates.

## Priority Logic

When multiple things could be done, prioritize:

1. **Failed phases** - Fix blockers first
2. **Paused work** - Resume interrupted work
3. **In-progress execution** - Continue what's started
4. **Next issue in active release** - Continue release progress
5. **Queue items** - Clear discovered items
6. **Planned issues not in releases** - Start new work (by priority label)
7. **No plans** - Suggest getting/planning issues

## State File Locations

| File | Purpose |
| ---- | ------- |
| `.tiki/state/current.json` | Active execution state |
| `.tiki/plans/issue-*.json` | All issue plans |
| `.tiki/queue/pending.json` | Items needing review |
| `.tiki/context/*.json` | Saved context for resume |
| `.tiki/releases/*.json` | Active releases |
| `.tiki/releases/archive/*.json` | Shipped (archived) releases |

## Comparison with /tiki:state

| `/tiki:state` | `/tiki:whats-next` |
| ------------- | ------------------ |
| Shows raw state data | Interprets state, suggests actions |
| Comprehensive overview | Focused on "what should I do" |
| Read-only display | Actionable recommendations |

## Notes

- This skill is read-only - never modifies state
- Suggestions are opinionated toward completing work
- Combines multiple state files into one actionable view
- For active releases: prioritize "planned" over "not_planned", consider requirements coverage
