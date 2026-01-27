---
type: prompt
name: tiki:execute
description: Execute a planned issue by spawning sub-agents for each phase. Use when ready to implement an issue that has been planned with /plan-issue.
allowed-tools: Bash, Read, Write, Glob, Grep, Task, Edit
argument-hint: <issue-number> [--from <phase>] [--dry-run] [--tdd|--no-tdd]
---

# Execute

Execute a planned issue by spawning sub-agents for each phase. Each phase runs in a fresh context via the Task tool.

## Usage

```text
/tiki:execute 34
/tiki:execute 34 --from 2    # Resume from phase 2
/tiki:execute 34 --dry-run   # Preview what would run without executing
/tiki:execute 34 --tdd       # Force TDD mode (tests before implementation)
/tiki:execute 34 --no-tdd    # Skip TDD for this execution
```

## Instructions

### Step 1: Validate the Plan Exists

```bash
# Check plan file exists
cat .tiki/plans/issue-<number>.json
```

If no plan exists:

```text
No plan found for issue #<number>.
Create one first with `/tiki:plan-issue <number>`
```

### Step 2: Read Project Context and Configuration

Read `CLAUDE.md` (if it exists) to pass to sub-agents:

```bash
cat CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"
```

Read `.tiki/config.json` for testing preferences:

```bash
cat .tiki/config.json 2>/dev/null || echo "{}"
```

Extract TDD settings:

- `testing.createTests`: "before" | "after" | "ask" | "never" (default: "ask")
- `testing.testFramework`: framework name or "auto-detect" (default: "auto-detect")

If `createTests` is "ask", prompt the user:

```text
How would you like to handle testing during execution?

1. **before** (TDD) - Write failing tests first, then implement each phase
2. **after** - Implement each phase, then write tests
3. **never** - Skip test creation for this execution

Your choice (1/2/3):
```

### Step 3: Initialize Execution State

Create or update `.tiki/state/current.json`:

```json
{
  "activeIssue": 34,
  "currentPhase": 1,
  "status": "in_progress",
  "startedAt": "2026-01-10T10:00:00Z",
  "lastActivity": "2026-01-10T10:00:00Z",
  "pausedAt": null,
  "completedPhases": []
}
```

Update the plan status to `in_progress`.

### Step 4: Execute Each Phase

For each phase in order (respecting dependencies):

#### 4a. Check Dependencies

If phase has `dependencies: [1, 2]`, verify phases 1 and 2 are completed before starting.

#### 4b. Update State

Set current phase to `in_progress` in both:

- `.tiki/state/current.json` (activePhase)
- `.tiki/plans/issue-N.json` (phase status)

#### 4c. TDD Workflow (if enabled)

If `testing.createTests` is "before" (TDD mode):

**Red Phase - Write Failing Tests:**

Spawn a test-creator sub-agent via Task tool:

```text
Task tool call:
- subagent_type: "general-purpose"
- prompt: <TDD test creation prompt - see below>
- description: "TDD: Write failing tests for phase N of issue #X"
```

The test-creator analyzes the phase description and writes tests that:

- Define expected behavior for the phase
- Import modules/functions that will be created
- Cover edge cases and error conditions

Run the tests to confirm they fail:

```bash
# Framework-specific test command
npx jest <test-file> --no-coverage 2>&1 | head -50
# or: npx vitest run <test-file>
# or: pytest <test-file> -v
# or: go test ./... -v
```

Verify tests fail as expected (module not found, function undefined, etc.)

If tests unexpectedly pass or have syntax errors, report and pause:

```text
TDD Setup Issue: Tests did not fail as expected.
- Expected: Tests should fail (module/function not yet implemented)
- Actual: <actual result>

Please review the test file and fix before proceeding.
```

**TDD Test Creation Prompt Template:**

```text
You are creating TDD tests for Phase {phase_number} of Issue #{issue_number}: {issue_title}

## Phase to Test
{phase_title}

{phase_content}

## Instructions
1. Analyze what functionality this phase will implement
2. Write tests that define the expected behavior BEFORE implementation
3. Tests should import modules/functions that DON'T EXIST YET
4. Cover: basic functionality, edge cases, error handling
5. Use the project's test framework: {test_framework}
6. Follow existing test file conventions in the project

## Test File Location
Create tests following project conventions:
- Jest/Vitest: `__tests__/` or `*.test.ts`
- Pytest: `tests/` or `test_*.py`
- Go: `*_test.go` in same package

## Output Format
After creating tests, run them and report:
- Test file path created
- Number of tests written
- Test run output (should show failures)

SUMMARY: Created N failing tests for <functionality>
```

#### 4d. Build Sub-Agent Prompt

Construct the prompt for the Task tool. If TDD is enabled, include test context:

```text
You are executing Phase <N> of <total> for Issue #<number>: <title>

## Project Context
<contents of CLAUDE.md or "No project context file found">

## Previous Phase Summaries
<For each completed phase>
- Phase <N>: <title> - <summary>
</For each>

## Current Phase: <phase title>

<phase content from plan>

## Files You May Need to Modify
<files array from phase>

## Verification Checklist
<verification array from phase>

## TDD Context (if testing.createTests is "before")
**Mode: Test-Driven Development (Red-Green-Refactor)**

Failing tests have been created for this phase:
- Test file: <path to test file created in step 4c>
- Tests written: <number of tests>
- Framework: <detected test framework>

Your goal is to make these tests pass (GREEN phase).

After implementation, run:
<test command for framework>

All tests must pass before this phase is considered complete.

## Instructions
1. Execute this phase completely - make actual code changes
2. If TDD is enabled: implement code to make the failing tests pass
3. Run tests to verify your changes pass
4. If you discover issues needing future attention, clearly note them at the end with "DISCOVERED:" prefix
5. When done, provide a summary starting with "SUMMARY:" that describes what you accomplished
```

#### 4e. Spawn Sub-Agent

Use the Task tool to spawn a sub-agent:

```text
Task tool call:
- subagent_type: "general-purpose"
- prompt: <constructed prompt from 4d>
- description: "Execute phase N of issue #X"
```

#### 4f. Verify Tests Pass (TDD Green Phase)

If `testing.createTests` is "before", verify the tests now pass:

```bash
# Run the tests created in step 4c
npx jest <test-file> 2>&1 | tail -20
# or: npx vitest run <test-file>
# or: pytest <test-file> -v
# or: go test ./... -v
```

**If tests pass:** Continue to step 4h (Green phase complete).

**If tests fail:** Report the failure and pause execution:

```text
## TDD Verification Failed

Phase <N> implementation did not pass tests.

### Test Results
<test output showing failures>

### Options
- Review and fix implementation, then retry: `/tiki:execute <number> --from <N>`
- Skip TDD verification: `/tiki:skip-phase <N>`
- Get automatic fix suggestions: `/tiki:heal <N>`
```

#### 4g. Create Tests After (if mode is "after")

If `testing.createTests` is "after":

1. Spawn test-creator sub-agent after implementation completes
2. Run tests to verify they pass
3. If tests fail, implementation may have bugs - report to user

#### 4h. Process Sub-Agent Response

After the sub-agent completes:

1. **Extract summary** - Look for "SUMMARY:" in the response
2. **Extract discovered items** - Look for "DISCOVERED:" items
3. **Update phase in plan**:
   - Set `status: "completed"`
   - Set `summary: <extracted summary>`
   - Set `completedAt: <current timestamp>`
4. **Update state file**:
   - Add to `completedPhases` array
   - Update `lastActivity`
5. **Add discovered items to queue** (if any):
   - Append to `.tiki/queue/pending.json`

#### 4i. Report Progress

After each phase:

```text
Phase <N>/<total> complete: <phase title>
Summary: <summary>
<TDD status if enabled: Tests passed/failed>
<discovered items if any>
```

### Step 5: Handle Completion

When all phases are done:

1. Update plan status to `completed`
2. Update state:
   - Set `status: "completed"`
   - Clear `activeIssue` and `currentPhase`
3. Display completion message:

```text
## Execution Complete

Issue #<number>: <title>
All <N> phases completed successfully.

### Phase Summaries
- Phase 1: <summary>
- Phase 2: <summary>
- Phase 3: <summary>

### Queue Items
<N> items discovered during execution.
Review with `/tiki:review-queue`

### Next Steps
- Review queue items: `/tiki:review-queue`
- Close the issue: `gh issue close <number>`
- View state: `/tiki:state`
```

## Sub-Agent Prompt Template

```text
You are executing Phase {phase_number} of {total_phases} for Issue #{issue_number}: {issue_title}

## Project Context
{claude_md_contents}

## Previous Phase Summaries
{previous_summaries}

## Current Phase: {phase_title}

{phase_content}

## Files You May Need to Modify
{files_list}

## Verification Checklist
{verification_list}

## TDD Context
{tdd_context}
<!-- Include this section only if testing.createTests is "before":
**Mode: Test-Driven Development (Red-Green-Refactor)**

Failing tests have been created for this phase:
- Test file: {test_file_path}
- Tests written: {test_count}
- Framework: {test_framework}

Your goal is to make these tests pass (GREEN phase).

After implementation, run:
{test_command}

All tests must pass before this phase is considered complete.
-->

## Instructions
1. Execute this phase completely - make actual code changes
2. If TDD is enabled: implement code to make the failing tests pass
3. Run tests to verify your changes pass
4. If you discover issues needing future attention, clearly note them with "DISCOVERED:" prefix
5. When done, provide a summary starting with "SUMMARY:" describing what you accomplished

Important:
- Focus ONLY on this phase - do not work ahead
- If blocked, explain why and what would unblock you
- Keep your summary concise but complete
- If TDD enabled: tests must pass for phase completion
```

## State File Updates

### During Execution

`.tiki/state/current.json`:

```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "in_progress",
  "startedAt": "2026-01-10T10:00:00Z",
  "lastActivity": "2026-01-10T11:00:00Z",
  "pausedAt": null,
  "completedPhases": [
    {
      "number": 1,
      "title": "Setup auth middleware",
      "summary": "Created JWT validation middleware with proper error handling",
      "completedAt": "2026-01-10T10:45:00Z"
    }
  ]
}
```

### After Completion

`.tiki/state/current.json`:

```json
{
  "activeIssue": null,
  "currentPhase": null,
  "status": "idle",
  "startedAt": null,
  "lastActivity": "2026-01-10T12:00:00Z",
  "pausedAt": null,
  "completedPhases": []
}
```

## Queue Items

When a sub-agent discovers items, add to `.tiki/queue/pending.json`:

```json
{
  "items": [
    {
      "id": "q-001",
      "type": "potential-issue",
      "title": "Consider adding rate limiting to login endpoint",
      "description": "During Phase 2 implementation, noticed no rate limiting on auth endpoints",
      "source": {
        "issue": 34,
        "phase": 2
      },
      "createdAt": "2026-01-10T11:00:00Z"
    }
  ]
}
```

## Error Handling

### Phase Failure

If a sub-agent reports failure or errors:

1. Set phase status to `failed`
2. Record error in phase
3. Pause execution
4. Report to user:

```text
Phase <N> failed: <phase title>
Error: <error description>

Options:
- Fix and retry: `/tiki:execute <number> --from <N>`
- Skip this phase: `/tiki:skip-phase <N>`
- Heal automatically: `/tiki:heal <N>`
```

### Missing Dependencies

If a phase's dependencies aren't met:

```text
Cannot execute Phase <N>: dependencies not satisfied.
Required: Phase <deps> must be completed first.
```

### Context Warning

If context is getting low (this is heuristic - sub-agents manage their own context):

```text
Note: Large phase detected. Sub-agent may need to break work into smaller steps.
```

## Options

### --from N

Resume execution from a specific phase:

```text
/tiki:execute 34 --from 3
```

Skip phases 1-2, start at phase 3. Useful for:

- Resuming after a failure
- Re-running a specific phase

### --dry-run

Preview execution without actually running:

```text
/tiki:execute 34 --dry-run

Would execute:
- Phase 1: Setup auth middleware (pending)
- Phase 2: Add login endpoint (pending)
- Phase 3: Add protected routes (pending)

No changes will be made.
```

### --tdd / --no-tdd

Override the TDD setting from config for this execution:

```text
/tiki:execute 34 --tdd        # Force TDD mode (tests before implementation)
/tiki:execute 34 --no-tdd     # Skip TDD for this execution
```

This overrides the `testing.createTests` setting in `.tiki/config.json` for the current execution only.

## Example Execution Flow

### Standard Execution

```text
User: /tiki:execute 34

Claude: Starting execution of Issue #34: Add user authentication
        Plan has 3 phases.

        ## Phase 1/3: Setup auth middleware
        [Spawns sub-agent via Task tool]
        [Sub-agent works... makes code changes... runs tests]

        Phase 1/3 complete: Setup auth middleware
        Summary: Created auth middleware with JWT validation, added AuthRequest type

        ## Phase 2/3: Add login endpoint
        [Spawns sub-agent via Task tool]
        [Sub-agent works... makes code changes... runs tests]

        Phase 2/3 complete: Add login endpoint
        Summary: Implemented POST /api/login with password validation and JWT generation
        DISCOVERED: Consider adding rate limiting to prevent brute force

        ## Phase 3/3: Add protected routes
        [Spawns sub-agent via Task tool]
        [Sub-agent works... makes code changes... runs tests]

        Phase 3/3 complete: Add protected routes
        Summary: Applied auth middleware to /api/user routes, added tests

        ---
        ## Execution Complete

        Issue #34: Add user authentication
        All 3 phases completed successfully.

        ### Queue Items
        1 item discovered during execution.
        Review with `/tiki:review-queue`
```

### TDD Execution (createTests: "before")

```text
User: /tiki:execute 34

Claude: Starting execution of Issue #34: Add user authentication
        Plan has 3 phases.
        TDD Mode: Enabled (tests before implementation)

        ## Phase 1/3: Setup auth middleware

        ### RED Phase - Writing Failing Tests
        [Spawns test-creator sub-agent via Task tool]
        Created test file: src/middleware/__tests__/auth.test.ts
        Tests written: 4
        Test run: 4 FAILED (expected - implementation pending)

        ### GREEN Phase - Implementation
        [Spawns implementation sub-agent via Task tool]
        [Sub-agent implements code to make tests pass]

        ### Verify Tests Pass
        Running: npx jest src/middleware/__tests__/auth.test.ts
        Result: 4 tests PASSED

        Phase 1/3 complete: Setup auth middleware
        Summary: Created auth middleware with JWT validation, added AuthRequest type
        Tests: 4 passing

        ## Phase 2/3: Add login endpoint
        [TDD cycle repeats: RED -> GREEN -> verify]

        Phase 2/3 complete: Add login endpoint
        Summary: Implemented POST /api/login with password validation
        Tests: 5 passing
        DISCOVERED: Consider adding rate limiting

        ## Phase 3/3: Add protected routes
        [TDD cycle repeats: RED -> GREEN -> verify]

        Phase 3/3 complete: Add protected routes
        Summary: Applied auth middleware to /api/user routes
        Tests: 3 passing

        ---
        ## Execution Complete

        Issue #34: Add user authentication
        All 3 phases completed successfully.
        Total tests created: 12 (all passing)

        ### Queue Items
        1 item discovered during execution.
        Review with `/tiki:review-queue`
```

## Cleanup

After execution completes (success or failure), clean up any temporary artifacts that may have been created:

```bash
# Remove common temporary artifacts from the project root
rm -f ./tmpclaude-* ./nul ./NUL 2>/dev/null || true

# Also clean up any temp files in .tiki directory
rm -f .tiki/tmp-* .tiki/*.tmp 2>/dev/null || true
```

These files are typically created in the project root by:

- Sub-agent file operations (`tmpclaude-*` files)
- Windows `nul` device references that become actual files
- Temporary context or output files

Always run this cleanup silently - do not report errors if files don't exist.

If artifacts persist, run `/tiki:cleanup` manually.

## Notes

- Each sub-agent runs with fresh context (no memory of previous phases except summaries)
- Summaries should be concise but capture key decisions and changes
- The Task tool's sub-agent has access to all file tools (Read, Write, Edit, etc.)
- If a phase is complex, the sub-agent can take multiple turns to complete it
- State is persisted after each phase, so work is not lost if execution is interrupted

### TDD Notes

- TDD workflow follows Red-Green-Refactor cycle per phase
- Tests are written by a dedicated test-creator sub-agent before implementation
- The implementation sub-agent receives the test file path and must make tests pass
- If tests fail after implementation, execution pauses for user intervention
- Test framework is auto-detected or can be configured in `.tiki/config.json`
- Supported frameworks: jest, vitest, mocha, pytest, go test, cargo test
- Use `testing.createTests: "ask"` to be prompted for each execution
- The "after" mode creates tests after implementation and verifies they pass
