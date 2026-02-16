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

Read `.tiki/state/current.json` and detect format version:

**v2 Format (has `version: 2` or `activeExecutions` array):**

1. Search `activeExecutions` for executions with `status: "paused"`
2. If issue number provided as argument:
   - Find execution where `issue` matches the provided number
   - Error if not found or not paused
3. If no issue number provided:
   - If exactly one paused execution: use it
   - If multiple paused executions: display selection

   ```
   Multiple paused executions found:

   [1] Issue #42: Add user authentication (paused 2h ago)
       Phase 3/5: Implement OAuth flow
   [2] Issue #57: Fix database connection (paused 1d ago)
       Phase 2/4: Add connection pooling

   Enter number to resume (or issue number): _
   ```

4. Store the selected execution object and its index in the array

**v1 Format (no `version` field or `version: 1`):**

1. Check top-level `status: "paused"`
2. If issue number provided, verify `activeIssue` matches
3. If no paused work found at top level, no paused work exists

**No Paused Work Found:**

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

Update `.tiki/state/current.json` based on format version:

**v2 Format:**

1. Find the execution in `activeExecutions` array by its index (from Step 1)
2. Update the execution object:
   - Set `status: "executing"`
   - Clear `pausedAt` (set to null)
   - Clear `pauseReason` (set to null)
   - Update `lastActivity` to current ISO timestamp

3. Update deprecated v1 fields for Tiki.Desktop compatibility:
   - Set top-level `status` to reflect aggregate state:
     - If any execution is `"executing"`: set to `"executing"`
     - Else if any execution is `"paused"`: set to `"paused"`
     - Else if any execution is `"failed"`: set to `"failed"`
     - Else: set to `"idle"`
   - Set `activeIssue` to the resumed execution's issue number
   - Set `currentPhase` to the resumed execution's currentPhase
   - Clear top-level `pausedAt` and `pauseReason` if this was the only paused execution
   - Update top-level `lastActivity`

**v1 Format:**

1. Update top-level fields:
   - Set `status: "executing"`
   - Clear `pausedAt` (set to null)
   - Clear `pauseReason` (set to null)
   - Update `lastActivity` to current ISO timestamp

**Update Plan File:**

Update phase status in `.tiki/plans/issue-N.json` to `"in_progress"`.

### Step 5: Continue Execution

Read `.tiki/prompts/resume/execution-options.md` for:

- Option A: Continue in current context (small remaining work)
- Option B: Spawn sub-agent with full context (substantial work)
- Completion handling and cleanup

### Step 6: Handle Edge Cases

If issues arise, read `.tiki/prompts/resume/edge-cases.md` for:

- Stale context warning (>7 days old)
- Stale execution warning (v2: check `isStale` flag or `staledAt` field)
- Context file missing handling
- Context file format reference
- Version migration (auto-migrate v1 to v2 if needed)

## Notes

- Context file is source of truth for resuming
- If in doubt, start fresh with `/tiki:execute --from N`
- Clean up context files after successful phase completion
