---
type: prompt
name: tiki:whats-next
description: Show current status and suggest next actions. Use when resuming work, checking progress, or deciding what to do next.
allowed-tools: Read, Glob, Bash
---

# What's Next

Display current Tiki state and provide actionable suggestions for what to do next. This is the go-to command when starting a session or resuming work.

## Usage

```
/tiki:whats-next
```

## Instructions

### Step 1: Gather State Information

Read all relevant state files:

1. **Current execution state**: `.tiki/state/current.json`
2. **All plans**: `.tiki/plans/issue-*.json`
3. **Queue items**: `.tiki/queue/pending.json`
4. **Saved context**: `.tiki/context/*.json`

### Step 2: Determine Current Situation

Analyze the state to understand what's happening:

| Situation | Indicators |
|-----------|------------|
| Active execution | `current.json` has `status: "in_progress"` |
| Paused work | `current.json` has `pausedAt` set |
| Failed phase | Plan has a phase with `status: "failed"` |
| Planned but not started | Plans exist with `status: "planned"` |
| Queue needs review | `pending.json` has items |
| Nothing in progress | No active state, no pending plans |

### Step 3: Build Recommendations

Based on the situation, provide specific actionable suggestions.

## Output Format

### When Work is In Progress

```
## What's Next

### Currently Active
**Issue #34:** Add user authentication
- Phase 2 of 3: Add login endpoint
- Status: in_progress
- Last activity: 15 minutes ago

### Suggested Action
Continue execution:
```
/tiki:execute 34
```

### Also Pending
- **Issue #35:** Fix login redirect (planned, 1 phase)
- **Queue:** 2 items need review
```

### When Work is Paused

```
## What's Next

### Paused Work
**Issue #34:** Add user authentication
- Paused at: Phase 2 of 3
- Paused: 2 hours ago
- Reason: Context limit reached

### Suggested Action
Resume where you left off:
```
/tiki:resume 34
```

Or start fresh from the current phase:
```
/tiki:execute 34 --from 2
```
```

### When a Phase Failed

```
## What's Next

### Failed Execution
**Issue #34:** Add user authentication
- Phase 2 failed: Add login endpoint
- Error: TypeScript compilation error in auth.ts

### Suggested Actions
1. **Heal automatically:**
   ```
   /tiki:heal 34
   ```

2. **Fix manually and retry:**
   ```
   /tiki:execute 34 --from 2
   ```

3. **Skip this phase:**
   ```
   /tiki:skip-phase 2
   ```
```

### When Plans Exist But Not Started

```
## What's Next

### Ready to Execute
| Issue | Title | Phases | Priority |
|-------|-------|--------|----------|
| #34 | Add user authentication | 3 | high |
| #35 | Fix login redirect | 1 | medium |

### Suggested Action
Start with the highest priority:
```
/tiki:execute 34
```

Or review the plan first:
```
/tiki:state
```
```

### When Queue Needs Attention

```
## What's Next

### Queue Items (3)
Items discovered during execution need your review:
- 1 potential new issue
- 2 questions needing input

### Suggested Action
Review and process the queue:
```
/tiki:review-queue
```
```

### When Nothing is Happening

```
## What's Next

### Current State
No active work. No planned issues.

### Suggested Actions
1. **View open GitHub issues:**
   ```bash
   gh issue list
   ```

2. **Get a specific issue:**
   ```
   /tiki:get-issue <number>
   ```

3. **Plan an issue for execution:**
   ```
   /tiki:plan-issue <number>
   ```
```

### Combined Example (Multiple Things Happening)

```
## What's Next

### Currently Active
**Issue #34:** Add user authentication
- Phase 2 of 3: Add login endpoint
- Status: in_progress
- Last activity: 15 minutes ago

### Queue (2 items)
Items need review after current work completes.

### Also Planned
- **Issue #35:** Fix login redirect (1 phase)
- **Issue #36:** Update documentation (2 phases)

### Suggested Action
Continue the active execution:
```
/tiki:execute 34
```

After completion, review queue items:
```
/tiki:review-queue
```
```

## Priority Logic

When multiple things could be done, prioritize suggestions in this order:

1. **Failed phases** - Fix blockers first
2. **Paused work** - Resume interrupted work
3. **In-progress execution** - Continue what's started
4. **Queue items** - Clear discovered items
5. **Planned issues** - Start new work (by priority label)
6. **No plans** - Suggest getting/planning issues

## State File Locations

| File | Purpose |
|------|---------|
| `.tiki/state/current.json` | Active execution state |
| `.tiki/plans/issue-*.json` | All issue plans |
| `.tiki/queue/pending.json` | Items needing review |
| `.tiki/context/*.json` | Saved context for resume |

## Comparison with /tiki:state

| `/tiki:state` | `/tiki:whats-next` |
|----------|---------------|
| Shows raw state data | Interprets state and suggests actions |
| Comprehensive overview | Focused on "what should I do" |
| Read-only display | Actionable recommendations |
| For understanding status | For deciding next steps |

Use `/tiki:state` when you want to see everything. Use `/tiki:whats-next` when you want guidance.

## Notes

- This skill is read-only - it never modifies state
- Suggestions are opinionated - they guide you toward completing work
- Good for session start or after being away from the project
- Combines information from multiple state files into one view
