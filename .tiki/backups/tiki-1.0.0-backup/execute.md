
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

### Step 3: Initialize State

Create/update `.tiki/state/current.json`. State format: see `.tiki/schemas/state.schema.json`

```json
{
  "activeIssue": <number>,
  "currentPhase": 1,
  "status": "in_progress",
  "startedAt": "<ISO timestamp>",
  "completedPhases": []
}
```

### Step 4: Execute Each Phase

For each phase (respecting dependencies):

#### 4a. Check for Subtasks

If `phase.subtasks` exists and has items:
  - Read `.tiki/prompts/execute/subtask-execution.md`
  - Use parallel execution flow (spawn multiple sub-agents per wave)

Otherwise, continue with standard single-agent execution.

#### 4b. Check Dependencies

Verify dependent phases are completed before starting.

#### 4c. Update State

Set phase status to `in_progress` in state and plan files.

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

#### 4h. Tests After (if mode is "after")

Spawn test-creator sub-agent after implementation, verify tests pass.

#### 4i. Process Response

1. Extract `SUMMARY:` from response
2. Extract `DISCOVERED:` items → add to `.tiki/queue/pending.json`
3. Extract `ASSUMPTION_INVALID:` markers → add to queue as invalid-assumption type
4. Extract `ADR_TRIGGER:` and `CONVENTION_TRIGGER:` markers → add to `.tiki/triggers/pending.json`
5. Extract `KNOWLEDGE:` markers → create entries in `.tiki/knowledge/entries/`
   - Format: `KNOWLEDGE: {"title": "...", "summary": "...", "keywords": [...]}`
   - See `.tiki/prompts/execute/knowledge-capture.md` for processing details
6. Update phase: `status: "completed"`, `summary`, `completedAt`
7. Update state: add to `completedPhases`, update `lastActivity`

#### 4j. Report Progress

```text
Phase N/total complete: <title>
Summary: <summary>
<TDD status if enabled>
<discovered items if any>
```

### Step 5: Handle Completion

When all phases complete:

1. Update plan status to `completed`
2. Update state: `status: "idle"`, clear `activeIssue`
3. Display completion summary with phase summaries and queue item count
4. Offer next steps: `/tiki:ship`, `/tiki:review-queue`, `/tiki:state`

## Sub-Agent Prompt Template

```text
You are executing Phase {N} of {total} for Issue #{number}: {title}

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
