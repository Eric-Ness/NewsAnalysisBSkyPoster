---
type: prompt
name: tiki:resume
description: Resume paused work with full context restoration. Use when continuing work that was previously paused.
allowed-tools: Read, Write, Glob, Bash, Task, Edit, Grep
argument-hint: [issue-number]
---

# Resume

Resume paused execution by loading saved context and continuing from where work left off.

## Usage

```
/tiki:resume
/tiki:resume 34
```

## Instructions

### Step 1: Find Paused Work

If no issue number provided, read `.tiki/state/current.json` for `status: "paused"`.
If issue number provided, verify it has paused state.

If no paused work found:
```
No paused work found.

Use `/tiki:state` to see current status.
Use `/tiki:execute <number>` to start execution.
```

### Step 2: Load Context

Read saved context from `.tiki/context/issue-N-phase-M.json` for:

- Progress (completed tasks, remaining tasks)
- Decisions made during previous session
- Notes and previous phase summaries

### Step 3: Verify and Display

Read `.tiki/prompts/resume/context-verification.md` for:

- File state verification (git status check)
- Context conflict handling options
- Context summary display format

### Step 4: Update State

Update `.tiki/state/current.json`:
- Set `status: "in_progress"`
- Clear `pausedAt`
- Update `lastActivity`

Update phase status in plan file to `"in_progress"`.

### Step 5: Continue Execution

Read `.tiki/prompts/resume/execution-options.md` for:

- Option A: Continue in current context (small remaining work)
- Option B: Spawn sub-agent with full context (substantial work)
- Completion handling and cleanup

### Step 6: Handle Edge Cases

If issues arise, read `.tiki/prompts/resume/edge-cases.md` for:

- Multiple paused issues handling
- Stale context warning (>7 days)
- Context file missing handling
- Context file format reference

## Notes

- Context file is source of truth for resuming
- If in doubt, start fresh with `/tiki:execute --from N`
- Clean up context files after successful phase completion
