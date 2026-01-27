# Subtask Execution

Conditional prompt loaded when `phase.subtasks` exists and has items.

## Parallel Execution Flow

1. Group subtasks into waves by dependency (Kahn's algorithm)
2. Execute each wave in parallel via Task tool with `run_in_background`
3. Collect results via TaskOutput
4. Proceed to next wave or handle failures

## Wave Grouping Algorithm

Use topological sort to group subtasks into execution waves:

1. Build dependency graph with in-degree counts
2. Find all tasks with in-degree 0 (no unmet dependencies) - these form wave 1
3. After wave execution, decrement in-degree for dependent tasks
4. Repeat until all tasks grouped or circular dependency detected

**Circular Dependency:** If no tasks have in-degree 0 but tasks remain, report cycle and halt.

## Wave Execution Pattern

For each wave:

```text
Wave 1 with 3 tasks:
- Task 2a: run_in_background: true
- Task 2b: run_in_background: true
- Task 2c: (last task synchronous - ensures wave completion)
```

**Single Subtask Optimization:** If only one subtask exists, skip parallelization overhead.

## Subtask Prompt Template

```text
You are executing Subtask {subtask_id} of Phase {phase_number} for Issue #{issue_number}

## Project Context
{claude_md_contents}

## Phase Context
Part of Phase {phase_number}: {phase_title}

## Your Subtask: {subtask_title}
{subtask_content}

## Files You May Modify
{subtask_files}

## Dependencies Completed
{completed_dependencies_summaries}

## Instructions
1. Execute ONLY this subtask
2. Focus on specific files listed
3. Flag incorrect assumptions: `ASSUMPTION_INVALID: {id} - {reason}`
4. Note discoveries: `DISCOVERED: <item>`
5. Provide summary: `TASK_SUMMARY: <what you accomplished>`
```

## Result Collection

After wave completion:

1. Use TaskOutput to retrieve background task results (timeout: 5 min)
2. Extract `TASK_SUMMARY:` from each result
3. Collect `DISCOVERED:` and `ASSUMPTION_INVALID:` items
4. Update subtask status: `completed` or `failed`
5. Merge summaries into phase summary

**TASK_SUMMARY Format:** Required prefix for result extraction. Keep concise (1-3 sentences).

## Failure Handling

### Partial Success

When some tasks succeed, some fail:
- Mark completed/failed status per subtask
- Identify blocked tasks (depend on failed tasks)
- Offer retry option: `--from {phase} --subtask {failed_id}`

### All Tasks Fail

Report all errors, suggest:
- Retry: `/tiki:execute {number} --from {phase}`
- Diagnose: `/tiki:heal {phase}`
- Skip: `/tiki:skip-phase {phase}`

### Task Timeout

If TaskOutput times out, task may still be running. Options: increase timeout, check manually, or retry subtask.

## Subtask State Tracking

```json
{
  "id": "2a",
  "status": "completed",
  "startedAt": "<ISO timestamp>",
  "completedAt": "<ISO timestamp>",
  "summary": "<TASK_SUMMARY content>"
}
```

Status values: `pending`, `in_progress`, `completed`, `failed`
