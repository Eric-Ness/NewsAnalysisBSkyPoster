
---
type: prompt
name: tiki:execute
description: Execute a planned issue by spawning sub-agents for each phase. Use when ready to implement an issue that has been planned with /plan-issue.
allowed-tools: Bash, Read, Write, Glob, Grep, Task, Edit, TaskOutput
argument-hint: <issue-number> [--from <phase>] [--dry-run] [--tdd|--no-tdd] [--subtask <id>]
---

# Execute

Execute a planned issue by spawning sub-agents for each phase. Each phase runs in a fresh context via the Task tool.

## Usage

```text
/tiki:execute 34
/tiki:execute 34 --from 2         # Resume from phase 2
/tiki:execute 34 --dry-run        # Preview without executing
/tiki:execute 34 --tdd            # Force TDD mode
/tiki:execute 34 --no-tdd         # Skip TDD
/tiki:execute 34 --from 2 --subtask 2b  # Retry specific subtask
```

## Instructions

### Step 1: Validate Plan

Read `.tiki/plans/issue-<number>.json`. If missing, prompt: "No plan found. Create one with `/tiki:plan-issue <number>`"

### Step 2: Load Context and Config

1. Read `CLAUDE.md` (pass to sub-agents)
2. Read `.tiki/config.json` for settings:
   - `testing.createTests`: "before"|"after"|"ask"|"never" (default: "ask")
   - `autoFix.enabled`: true|false|"prompt" (default: "prompt")
   - `autoFix.maxAttempts`: max fix attempts (default: 3)

If `createTests` is "ask", prompt user for TDD preference (before/after/never).

### Step 3: Initialize State (v2 Multi-Execution)

Read `.tiki/state/current.json` if it exists. State format: see `.tiki/schemas/state.schema.json`

#### 3a. Version Detection and Migration

Check state version per `.tiki/prompts/state/migration.md`:
- No `version` field or `version: 1` = v1 state, needs migration
- `version: 2` = v2 state, ready for use
- Empty/missing file = create fresh v2 state

If v1 detected, migrate to v2:
1. Extract existing execution data from flat fields
2. Create execution object with ID `exec-{issue}-migrated`
3. Place in `activeExecutions` array
4. Preserve deprecated v1 fields for compatibility

#### 3b. Check for Existing Execution

Search `activeExecutions` array for execution with matching issue number:

```javascript
const existing = state.activeExecutions.find(e => e.issue === issueNumber);
```

**If existing execution found with `status: "executing"`:**

Display warning and prompt user:

```
### Warning: Existing Execution

Issue #45 already has an active execution:
- Execution ID: exec-45-a1b2c3d4
- Started: 10 minutes ago
- Current phase: 2 of 5
- Status: executing

Options:
- [R]esume existing execution
- [C]ancel existing and start fresh
- [A]bort
```

Use AskUserQuestion tool to get user choice:
- **Resume**: Use existing execution, continue from current phase
- **Cancel**: Remove existing from `activeExecutions`, create new execution
- **Abort**: Exit without changes

**If existing execution found with `status: "paused"` or `status: "failed"`:**
- Resume: reactivate the existing execution
- Cancel: remove and create fresh

#### 3c. Generate Execution ID

For new executions, generate unique ID:

```javascript
const executionId = `exec-${issueNumber}-${crypto.randomUUID().slice(0, 8)}`;
// Example: exec-45-a1b2c3d4
```

Store this execution ID for all subsequent state updates in this session.

#### 3d. Create Execution Object

Add new execution to `activeExecutions` array:

```json
{
  "id": "exec-45-a1b2c3d4",
  "issue": 45,
  "issueTitle": "Add user authentication",
  "currentPhase": 1,
  "totalPhases": 5,
  "status": "executing",
  "startedAt": "<ISO timestamp>",
  "pausedAt": null,
  "pauseReason": null,
  "completedPhases": [],
  "failedPhase": null,
  "errorMessage": null,
  "autoFixAttempt": 0,
  "autoFixMaxAttempts": null,
  "activeHook": null,
  "activeSubtasks": [],
  "lastActivity": "<ISO timestamp>",
  "isStale": false,
  "staledAt": null,
  "planFile": ".tiki/plans/issue-45.json"
}
```

#### 3e. Update Deprecated v1 Fields (CRITICAL for Tiki.Desktop)

After modifying `activeExecutions`, you MUST sync deprecated top-level fields for Tiki.Desktop compatibility. Follow these steps exactly:

**Step 3e.1: Find the active execution to sync from:**
```javascript
const firstActive = state.activeExecutions.find(e => e.status === 'executing')
  || state.activeExecutions[0];
```

**Step 3e.2: Sync each deprecated field:**
```javascript
state.activeIssue = firstActive?.issue || null;
state.currentPhase = firstActive?.currentPhase || null;
state.status = calculateAggregateStatus(state.activeExecutions);
state.startedAt = firstActive?.startedAt || null;
state.lastActivity = firstActive?.lastActivity || new Date().toISOString();
```

**Step 3e.3: CRITICAL - Initialize top-level completedPhases array:**
```javascript
// Top-level completedPhases MUST be an array of phase NUMBERS (integers)
// NOT phase objects - the mapping is required!
state.completedPhases = firstActive?.completedPhases?.map(p =>
  typeof p === 'object' ? p.number : p
) || [];
```

Aggregate status priority: `failed` > `paused` > `executing` > `idle`

**Expected State Structure After Initialization:**

The state file should look like this (showing both levels of completedPhases):

```json
{
  "version": 2,
  "status": "executing",
  "activeIssue": 45,
  "currentPhase": 1,
  "completedPhases": [],          // <-- TOP-LEVEL: array of integers
  "startedAt": "2026-01-30T10:00:00.000Z",
  "lastActivity": "2026-01-30T10:00:00.000Z",
  "activeExecutions": [
    {
      "id": "exec-45-a1b2c3d4",
      "issue": 45,
      "currentPhase": 1,
      "completedPhases": [],      // <-- EXECUTION-LEVEL: will contain objects
      "status": "executing"
    }
  ]
}
```

**State Updates Summary:**
1. Ensure `version: 2` in state
2. Generate execution ID: `exec-{issue}-{8-char-uuid}`
3. Add execution object to `activeExecutions` array
4. Set execution's `currentPhase` to 1 (or starting phase if using `--from`)
5. Set execution's `status` to `"executing"`
6. Set execution's `startedAt` and `lastActivity` to current ISO timestamp
7. Initialize execution's `completedPhases` to `[]` (or preserve if resuming)
8. **CRITICAL: Initialize top-level `state.completedPhases` to `[]`**
9. Sync all other deprecated v1 fields from active execution

### Step 3.5: Pre-Execute Hook (Conditional)

**Only execute if:** `.tiki/hooks/pre-execute` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `pre-execute` hook with:
- `TIKI_ISSUE_NUMBER`: Issue number
- `TIKI_ISSUE_TITLE`: Issue title (sanitized)
- `TIKI_TOTAL_PHASES`: Total phase count

If hook fails (non-zero exit or timeout), abort execution and show error message.

**State Updates (Execution-Scoped):**
1. Find execution by ID in `activeExecutions`
2. Before hook: Set execution's `activeHook: "pre-execute"`, update `lastActivity`
3. After hook success: Set execution's `activeHook: null`
4. After hook failure: Set execution's `status: "failed"`, `errorMessage: "<hook error>"`, `activeHook: null`
5. Sync deprecated v1 fields

### Step 4: Execute Each Phase

For each phase (respecting dependencies):

#### 4a. Check for Subtasks

If `phase.subtasks` exists and has items:
  - Read `.tiki/prompts/execute/subtask-execution.md`
  - Use parallel execution flow (spawn multiple sub-agents per wave)

Otherwise, continue with standard single-agent execution.

#### 4b. Check Dependencies

Verify dependent phases are completed before starting.

#### 4b.5. Phase-Start Hook (Conditional)

**Only execute if:** `.tiki/hooks/phase-start` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `phase-start` hook with:
- `TIKI_ISSUE_NUMBER`: Issue number
- `TIKI_PHASE_NUMBER`: Current phase number
- `TIKI_PHASE_TITLE`: Current phase title (sanitized)

If hook fails (non-zero exit or timeout), abort execution and show error message.

**State Updates (Execution-Scoped):**
1. Find execution by ID in `activeExecutions`
2. Before hook: Set execution's `activeHook: "phase-start"`, update `lastActivity`
3. After hook success: Set execution's `activeHook: null`
4. After hook failure: Set execution's `status: "failed"`, `errorMessage: "<hook error>"`, `activeHook: null`
5. Sync deprecated v1 fields

#### 4c. Update State (Execution-Scoped)

Set phase status to `in_progress` in state and plan files.

Find execution by ID (stored from Step 3), not by `activeIssue`:

```javascript
const execution = state.activeExecutions.find(e => e.id === executionId);
```

**State Updates:**
1. Find execution in `activeExecutions` by execution ID
2. Set execution's `currentPhase` to current phase number
3. Update execution's `lastActivity` to current ISO timestamp
4. Update plan file: set phase's `status` to `"in_progress"`
5. Sync deprecated v1 fields (`activeIssue`, `currentPhase`, `status`, `lastActivity`)

#### 4d. TDD Workflow

If `testing.createTests` is "before":
  - Read `.tiki/prompts/execute/tdd-workflow.md`
  - Spawn test-creator sub-agent to write failing tests
  - Verify tests fail as expected before implementation

#### 4e. Build Sub-Agent Prompt

Construct prompt with:
- CLAUDE.md contents
- Previous phase summaries
- Current phase content and files
- Filtered assumptions (by `affectsPhases`)
- Verification checklist
- TDD context (if enabled)

See Sub-Agent Prompt Template section below.

#### 4f. Spawn Sub-Agent

```text
Task tool call:
- subagent_type: "general-purpose"
- prompt: <constructed prompt>
- description: "Execute phase N of issue #X"
```

#### 4g. Handle Verification

Run phase verification steps. On failure:

If `autoFix.enabled`:
  - Read `.tiki/prompts/execute/autofix-strategies.md`
  - Execute 3-tier escalation: direct → contextual-analysis → approach-review
  - Record attempts in phase's `fixAttempts` array
  - On success: continue to next phase
  - On exhaustion: pause for manual intervention

If `autoFix.enabled` is "prompt": ask user on first failure.

**State Updates (Execution-Scoped):**
1. Find execution by ID in `activeExecutions`
2. On first verification failure: Set execution's `autoFixAttempt: 1`, `autoFixMaxAttempts` from config (default: 3)
3. On each retry: Increment execution's `autoFixAttempt`, update `lastActivity`
4. On fix success: Set execution's `autoFixAttempt: 0`, `autoFixMaxAttempts: null`, update `lastActivity`
5. On exhaustion (max attempts reached): Set execution's `status: "failed"`, `failedPhase: <N>`, `errorMessage: "<verification error>"`, clear `autoFixAttempt: null`, `autoFixMaxAttempts: null`
6. Sync deprecated v1 fields

#### 4h. Tests After (if mode is "after")

Spawn test-creator sub-agent after implementation, verify tests pass.

#### 4i. Process Response (Execution-Scoped)

1. Extract `SUMMARY:` from response
2. Extract `DISCOVERED:` items → add to `.tiki/queue/pending.json`
3. Extract `ASSUMPTION_INVALID:` markers → add to queue as invalid-assumption type
4. Extract `ADR_TRIGGER:` and `CONVENTION_TRIGGER:` markers → add to `.tiki/triggers/pending.json`
5. Extract `KNOWLEDGE:` markers → create entries in `.tiki/knowledge/entries/`
   - Format: `KNOWLEDGE: {"title": "...", "summary": "...", "keywords": [...]}`
   - See `.tiki/prompts/execute/knowledge-capture.md` for processing details
6. Update phase: `status: "completed"`, `summary`, `completedAt`
7. Update state: find execution by ID, add to that execution's `completedPhases`

Find execution by ID (stored from Step 3):

```javascript
const execution = state.activeExecutions.find(e => e.id === executionId);
```

**State Updates:**
1. Find execution in `activeExecutions` by execution ID
2. Add completed phase object to execution's `completedPhases` array:
   ```json
   { "number": N, "title": "Phase title", "completedAt": "<ISO>", "summary": "<summary>" }
   ```
3. Update execution's `lastActivity` to current ISO timestamp
4. If auto-fix was used: Clear execution's `autoFixAttempt: 0`, `autoFixMaxAttempts: null`
5. Sync deprecated v1 fields (see step 6 below)
6. **CRITICAL - Update top-level `completedPhases` array:**
   ```javascript
   // Extract phase numbers from execution's completedPhases objects
   state.completedPhases = execution.completedPhases.map(p =>
     typeof p === 'object' ? p.number : p
   );
   ```

**Example: After Phase 2 Completes**

Execution object contains phase objects:
```json
{
  "id": "exec-45-a1b2c3d4",
  "completedPhases": [
    { "number": 1, "title": "Setup", "completedAt": "...", "summary": "..." },
    { "number": 2, "title": "Core implementation", "completedAt": "...", "summary": "..." }
  ]
}
```

Top-level state MUST have phase numbers only:
```json
{
  "version": 2,
  "completedPhases": [1, 2],     // <-- INTEGERS, not objects!
  "activeIssue": 45,
  "currentPhase": 3,
  "activeExecutions": [...]
}
```

**Verification:** After writing state, confirm `state.completedPhases` exists at the top level and contains integers.

#### 4j. Phase-Complete Hook (Conditional)

**Only execute if:** `.tiki/hooks/phase-complete` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `phase-complete` hook with:
- `TIKI_ISSUE_NUMBER`: Issue number
- `TIKI_PHASE_NUMBER`: Completed phase number
- `TIKI_PHASE_TITLE`: Phase title (sanitized)
- `TIKI_PHASE_STATUS`: "completed" or "failed"

**Note:** Phase-complete failure logs warning but doesn't fail execution (phase work already done).

**State Updates (Execution-Scoped):**
1. Find execution by ID in `activeExecutions`
2. Before hook: Set execution's `activeHook: "phase-complete"`, update `lastActivity`
3. After hook (success or failure): Set execution's `activeHook: null`
4. Sync deprecated v1 fields

#### 4k. Report Progress

```text
Phase N/total complete: <title>
Summary: <summary>
<TDD status if enabled>
<discovered items if any>
```

### Step 5: Handle Completion (Move to History)

When all phases complete:

1. Update plan status to `completed`
2. Move execution from `activeExecutions` to `executionHistory`
3. Display completion summary with phase summaries and queue item count

Find execution by ID and move to history:

```javascript
// Find and remove from activeExecutions
const execIndex = state.activeExecutions.findIndex(e => e.id === executionId);
const execution = state.activeExecutions.splice(execIndex, 1)[0];

// Create archived execution for history
const archivedExecution = {
  id: execution.id,
  issue: execution.issue,
  issueTitle: execution.issueTitle,
  status: "completed",
  startedAt: execution.startedAt,
  endedAt: new Date().toISOString(),
  completedPhases: execution.completedPhases.length,
  totalPhases: execution.totalPhases,
  summary: generateCompletionSummary(execution)
};

// Add to history
state.executionHistory.push(archivedExecution);
```

**State Updates:**
1. Set execution's `status` to `"completed"` before archiving
2. Remove execution from `activeExecutions` array
3. Add archived execution to `executionHistory` array with:
   - Original `id`, `issue`, `issueTitle`
   - `status: "completed"`
   - `endedAt`: current ISO timestamp
   - `completedPhases`: count of completed phases
   - `totalPhases`: total phase count
   - `summary`: brief completion summary
4. Set `lastCompletedIssue` to the completed issue number
5. Set `lastCompletedAt` to current ISO timestamp
6. Update `lastActivity` to current ISO timestamp
7. Sync deprecated v1 fields from remaining active executions (if any):
   - If no remaining executions: set `status: "idle"`, clear `activeIssue`, `currentPhase`, etc.
   - If other executions remain: sync from first active execution

### Step 5.5: Post-Execute Hook (Conditional)

**Only execute if:** `.tiki/hooks/post-execute` (or `.sh`/`.ps1` on Windows) exists.

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow. On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run `post-execute` hook with:
- `TIKI_ISSUE_NUMBER`: Issue number
- `TIKI_ISSUE_TITLE`: Issue title (sanitized)
- `TIKI_PHASES_COMPLETED`: Count of completed phases

**Note:** Post-execute failure logs warning but doesn't fail (work already done).

### Step 6: Offer Next Steps

Offer next steps: `/tiki:ship`, `/tiki:review-queue`, `/tiki:state`

## Sub-Agent Prompt Template

```text
You are executing Phase {N} of {total} for Issue #{number}: {title}
Execution ID: {execution_id}

## Project Context
{claude_md_contents}

## Previous Phase Summaries
{previous_summaries}

## Current Phase: {phase_title}
{phase_content}

## Files You May Need to Modify
{files_list}

## Relevant Assumptions
{filtered_assumptions_by_confidence}

## Verification Checklist
{verification_list}

## TDD Context (if enabled)
{tdd_context}

## Instructions
1. Execute this phase completely - make actual code changes
2. If TDD enabled: implement to make failing tests pass
3. Run tests to verify changes
4. Flag incorrect assumptions: `ASSUMPTION_INVALID: {id} - {reason}`
5. Note discoveries: `DISCOVERED: <item>`
6. Emit knowledge when solving non-obvious problems: `KNOWLEDGE: {"title": "...", "summary": "...", "keywords": [...]}`
7. Provide summary: `SUMMARY: <what you accomplished>`
```

**Note:** The execution ID is passed to sub-agents for logging/debugging purposes. All state updates use this ID to locate the correct execution in the `activeExecutions` array.

## State Files

- `.tiki/state/current.json` - Active execution state (see `.tiki/schemas/state.schema.json`)
- `.tiki/plans/issue-N.json` - Plan with phase status (see `.tiki/schemas/plan.schema.json`)
- `.tiki/queue/pending.json` - Discovered items (see `.tiki/schemas/queue.schema.json`)

## Error Handling

### Phase Failure

1. Set phase status to `failed`, record error
2. Check `.tiki/debug/index.json` for similar resolved sessions
3. If auto-fix enabled: attempt fix (see Step 4g)
4. Pause and report with recovery options

### Missing Dependencies

Report: "Cannot execute Phase N: dependencies not satisfied."

## Options

| Option | Description |
|--------|-------------|
| `--from N` | Resume from phase N (skip earlier phases) |
| `--dry-run` | Preview execution without running |
| `--tdd` | Force TDD mode for this execution |
| `--no-tdd` | Skip TDD for this execution |
| `--subtask ID` | Retry specific subtask (with `--from`) |

## Cleanup

After execution, remove temporary artifacts:
```bash
rm -f ./tmpclaude-* ./nul ./NUL .tiki/tmp-* .tiki/*.tmp 2>/dev/null || true
```

## Notes

- Each sub-agent runs with fresh context (only summaries from previous phases)
- Summaries should be concise but capture key decisions
- State persists after each phase (work not lost on interruption)
- For TDD details: see `.tiki/prompts/execute/tdd-workflow.md`
- For parallel execution: see `.tiki/prompts/execute/subtask-execution.md`
- For auto-fix strategies: see `.tiki/prompts/execute/autofix-strategies.md`
- For knowledge capture: see `.tiki/prompts/execute/knowledge-capture.md`
