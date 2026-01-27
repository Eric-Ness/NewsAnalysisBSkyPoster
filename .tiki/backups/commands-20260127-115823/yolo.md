---
type: prompt
name: tiki:yolo
description: Run the full Tiki workflow (get -> review -> plan -> audit -> execute -> review) with TDD enabled by default.
allowed-tools: Bash, Read, Write, Glob, Grep, Task, Edit, Skill
argument-hint: <issue-number> [--no-tdd] [--skip-review] [--force-review]
---

# YOLO Mode

Execute the complete Tiki workflow pipeline for an issue in one command. This orchestrates all steps from fetching the issue through execution and queue review.

## Usage

```text
/tiki:yolo 34
/tiki:yolo 34 --no-tdd        # Skip TDD mode
/tiki:yolo 34 --skip-review   # Skip the review step for simple issues
/tiki:yolo 34 --force-review  # Continue even if review finds blocking concerns
/tiki:yolo 34 --no-tdd --skip-review  # Skip both TDD and review
```

## Instructions

### Step 0: Validate Input

Parse the issue number and flags from user input:

```javascript
// Parse: /tiki:yolo 34 --no-tdd --skip-review --force-review
const issueNumber = args[0];  // Required
const noTdd = args.includes('--no-tdd');
const skipReview = args.includes('--skip-review');
const forceReview = args.includes('--force-review');
const tddEnabled = !noTdd;
const reviewEnabled = !skipReview;
```

If no issue number provided:

```text
YOLO mode requires an issue number.

Usage: /tiki:yolo <issue-number> [--no-tdd] [--skip-review] [--force-review]

Example: /tiki:yolo 34
```

### Step 1: Display Progress Header

Show the YOLO mode header with progress tracking:

```text
## YOLO Mode: Issue #<number>

Mode: TDD <enabled|disabled>, Review <enabled|skipped>, Force review <if set>

[1/6] Fetching issue...
```

Note: If `--skip-review` is used, show 5 steps instead of 6 and adjust step numbers accordingly.

### Step 2: Fetch the Issue

Use GitHub CLI to fetch the issue (same as `/tiki:get-issue`):

```bash
gh issue view <number> --json number,title,body,state,labels,assignees,milestone,createdAt,updatedAt,comments
```

**If issue not found:**
```text
[1/5] Fetching issue... FAILED

Issue #<number> not found.

Verify the issue number and try again.
```
Stop execution here.

**If successful:**
```text
[1/6] Fetching issue... OK
      Issue #<number>: <title>
      State: <open/closed>
      Labels: <labels or "None">

[2/6] Reviewing issue...
```

Display the issue title and key details, then continue to review (or planning if review is skipped).

### Step 2.5: Review the Issue (unless --skip-review)

**If review is enabled** (default), analyze the issue for concerns (same as `/tiki:review-issue --yolo`):

1. Analyze the issue for alternatives, assumptions, blockers, edge cases, scope, clarity, and risks
2. Explore relevant codebase if needed
3. Categorize findings by severity: **blocking**, **warning**, or **info**
4. If concerns are found, add a GitHub comment with recommendations
5. Determine verdict: `blocked`, `warnings`, or `clean`

#### Handle Review Verdict

**If verdict is "blocked" AND `--force-review` is NOT set:**

```text
[2/6] Reviewing issue... BLOCKED

### Blocking Concerns Found

1. **[Scope]**: This issue combines authentication AND authorization - these should be separate issues
   - Authentication: login, logout, session management
   - Authorization: roles, permissions, access control

These concerns must be addressed before planning can proceed.

### GitHub Comment
Added comment to issue #<number> with blocking concerns.

### Options
- Address the concerns and retry: `/tiki:yolo <number>`
- Override and continue anyway: `/tiki:yolo <number> --force-review`
- Skip review entirely: `/tiki:yolo <number> --skip-review`

YOLO mode paused. Resolve blocking concerns or use override flag.
```

**STOP execution here.** Do not proceed to planning.

**If verdict is "blocked" AND `--force-review` IS set:**

```text
[2/6] Reviewing issue... BLOCKED (overridden with --force-review)
      - Blocking: Issue should be split into auth + authz

      Proceeding despite blocking concerns (--force-review)

[3/6] Creating plan...
```

Continue to planning despite blocking concerns.

**If verdict is "warnings":**

```text
[2/6] Reviewing issue... OK (with warnings)
      - Warning: No rate limiting mentioned for login endpoint
      - Warning: Password policy not specified

      Proceeding despite warnings.

[3/6] Creating plan...
```

Continue to planning.

**If verdict is "clean":**

```text
[2/6] Reviewing issue... OK (no concerns)
      Issue is well-defined, ready to plan.

[3/6] Creating plan...
```

Continue to planning.

**If review is skipped:**

```text
[2/5] Reviewing issue... SKIPPED
```

Then continue to planning.

### Step 3: Create the Plan

**Step number:** 3/6 (or 2/5 if review skipped)

Generate a phased execution plan (same as `/tiki:plan-issue`):

1. Analyze the issue content
2. Explore the codebase to understand context
3. Break into appropriately-sized phases
4. Create `.tiki/plans/issue-<number>.json`

**If planning fails:**

```text
[3/6] Creating plan... FAILED

Could not generate a plan for this issue.
Reason: <specific error>

Try running `/tiki:plan-issue <number>` manually for more control.
```
Stop execution here.

**If successful:**

```text
[3/6] Creating plan... OK
      Phases: <N>
      - Phase 1: <title>
      - Phase 2: <title>
      - ...

[4/6] Auditing plan...
```

### Step 4: Audit the Plan

**Step number:** 4/6 (or 3/5 if review skipped)

Validate the plan for issues (same as `/tiki:audit-plan`):

1. Check phase sizes and complexity
2. Validate dependencies (no circular refs)
3. Detect file conflicts
4. Verify referenced files exist
5. Ensure verification steps exist

Collect errors and warnings.

**If blocking errors found:**

```text
[4/6] Auditing plan... BLOCKED

Plan has blocking issues:
- <error 1>
- <error 2>

Run `/tiki:plan-issue <number>` to revise the plan, then retry.
```
Stop execution here.

**If warnings only:**

```text
[4/6] Auditing plan... OK (with warnings)
      - <warning 1>
      - <warning 2>

      Proceeding despite warnings.

[5/6] Executing phases (TDD: <enabled/disabled>)...
```

**If clean:**

```text
[4/6] Auditing plan... OK

[5/6] Executing phases (TDD: <enabled/disabled>)...
```

### Step 5: Execute the Phases

**Step number:** 5/6 (or 4/5 if review skipped)

Execute all phases sequentially (same as `/tiki:execute`):

1. Read project context (CLAUDE.md if exists)
2. Initialize execution state
3. For each phase:
   - If TDD enabled: Run Red phase (create failing tests)
   - Spawn sub-agent via Task tool
   - If TDD enabled: Verify tests pass (Green phase)
   - Extract summary and discovered items
   - Update state files
   - Report progress

Pass the TDD flag based on user input:
- Default: `--tdd` (TDD enabled)
- With `--no-tdd`: Skip TDD mode

**Progress display during execution:**

```text
[5/6] Executing phases (TDD: enabled)...
      Phase 1/3: <title>... DONE
      Phase 2/3: <title>... DONE
      Phase 3/3: <title>... DONE
```

**If execution fails:**

```text
[5/6] Executing phases... FAILED at Phase <N>

Phase <N> failed: <title>
Error: <error description>

Options:
- Fix and retry: `/tiki:execute <number> --from <N>`
- Auto-heal: `/tiki:heal <N>`
- Skip this phase: `/tiki:skip-phase <N>`
```
Stop execution here (do not proceed to queue review).

**If successful:**

```text
[5/6] Executing phases... OK
      All <N> phases completed.

[6/6] Reviewing queue...
```

### Step 6: Review Queue

**Step number:** 6/6 (or 5/5 if review skipped)

Check for items discovered during execution (same as `/tiki:review-queue`):

1. Read `.tiki/queue/pending.json`
2. Display any items found
3. Prompt user for action on each item

**If queue is empty:**

```text
[6/6] Reviewing queue... OK (0 items)

---

## YOLO Complete!

Issue #<number>: <title>
All <N> phases completed successfully.
TDD: <enabled/disabled>
Queue: Empty

### Phase Summaries
- Phase 1: <summary>
- Phase 2: <summary>
- Phase 3: <summary>

### Next Steps
- Close the issue: `gh issue close <number>`
- View state: `/tiki:state`
```

**If queue has items:**

```text
[6/6] Reviewing queue... <N> items found

### Queue Items Discovered

1. <item title>
   Source: Phase <N>
   Type: <type>

2. <item title>
   Source: Phase <N>
   Type: <type>

Actions:
- Create issues from all: `/tiki:review-queue --create-all`
- Review individually: `/tiki:review-queue`
- Dismiss all: `/tiki:review-queue --dismiss-all`

---

## YOLO Complete!

Issue #<number>: <title>
All <N> phases completed successfully.
TDD: <enabled/disabled>
Queue: <N> items pending review

### Phase Summaries
- Phase 1: <summary>
- Phase 2: <summary>
- Phase 3: <summary>

### Next Steps
- Review queue items: `/tiki:review-queue`
- Close the issue: `gh issue close <number>`
```

## Error Handling

### Issue Not Found

```text
## YOLO Mode: Issue #<number>

[1/6] Fetching issue... FAILED

Issue #<number> not found.

Verify the issue number exists:
  gh issue list

Or check if you're in the correct repository.
```

### Review Blocking Concerns

```text
## YOLO Mode: Issue #<number>

[1/6] Fetching issue... OK
[2/6] Reviewing issue... BLOCKED

### Blocking Concerns Found

1. **[Scope]**: This issue should be split...

These concerns must be addressed before planning can proceed.

### Options
- Address the concerns and retry: `/tiki:yolo <number>`
- Override and continue anyway: `/tiki:yolo <number> --force-review`
- Skip review entirely: `/tiki:yolo <number> --skip-review`

YOLO mode paused.
```

This is NOT a failure - the review identified valid concerns that should be addressed. Use `--force-review` to override if you want to proceed anyway.

### Planning Failure

```text
## YOLO Mode: Issue #<number>

[1/6] Fetching issue... OK
[2/6] Reviewing issue... OK
[3/6] Creating plan... FAILED

Failed to create execution plan.

Possible causes:
- Issue description is unclear or empty
- Codebase analysis encountered errors

Try:
- `/tiki:plan-issue <number>` for manual planning
- Review the issue description for clarity
```

### Audit Blocking Errors

```text
## YOLO Mode: Issue #<number>

[1/6] Fetching issue... OK
[2/6] Reviewing issue... OK
[3/6] Creating plan... OK
[4/6] Auditing plan... BLOCKED

The plan has blocking issues that prevent execution:

Errors:
- Circular dependency: Phase 2 -> Phase 4 -> Phase 2
- Phase 3 references non-existent file: src/old/api.ts

Resolution required. Run `/tiki:plan-issue <number>` to revise.
```

### Execution Failure

```text
## YOLO Mode: Issue #<number>

[1/6] Fetching issue... OK
[2/6] Reviewing issue... OK
[3/6] Creating plan... OK
[4/6] Auditing plan... OK
[5/6] Executing phases... FAILED at Phase 2

Phase 2 of 3 failed: Add login endpoint

Error: TypeScript compilation error in src/routes/auth.ts

Progress saved. Phases 1 completed successfully.

Options:
- Auto-heal: `/tiki:heal` - attempts automatic fix
- Manual fix: Fix the error, then `/tiki:execute <number> --from 2`
- Skip phase: `/tiki:skip-phase 2`

Queue review skipped due to execution failure.
```

### TDD Test Failure

```text
## YOLO Mode: Issue #<number>

[1/6] Fetching issue... OK
[2/6] Reviewing issue... OK
[3/6] Creating plan... OK
[4/6] Auditing plan... OK
[5/6] Executing phases... FAILED at Phase 2 (TDD verification)

Phase 2 implementation did not pass tests.

Test Results:
  FAIL src/routes/__tests__/auth.test.ts
    - should validate JWT token (expected 401, got 500)
    - should attach user to request (undefined is not assignable)

Options:
- Auto-heal: `/tiki:heal` - attempts automatic fix
- Manual fix: Review and fix implementation, then `/tiki:execute <number> --from 2`
```

## Options

### --no-tdd

Skip Test-Driven Development mode for this execution:

```text
/tiki:yolo 34 --no-tdd
```

This executes phases without creating tests first. Use when:

- The issue is purely documentation or configuration
- Tests already exist and don't need expansion
- You want faster execution without TDD overhead

Default behavior (without flag): TDD is enabled.

### --skip-review

Skip the pre-planning review step:

```text
/tiki:yolo 34 --skip-review
```

This skips the issue review step and goes directly to planning. Use when:

- The issue is simple and well-defined
- You've already reviewed the issue manually
- You want faster execution for straightforward tasks

Default behavior (without flag): Review is enabled.

### --force-review

Override blocking concerns from review and continue anyway:

```text
/tiki:yolo 34 --force-review
```

When the review step finds blocking concerns, YOLO normally pauses and asks for resolution. This flag overrides that behavior and forces the pipeline to continue. Use when:

- You understand the blocking concern but want to proceed anyway
- You plan to address the concern during implementation
- You believe the blocking concern is a false positive

Default behavior (without flag): YOLO pauses on blocking concerns.

**Warning:** Using `--force-review` may lead to suboptimal plans or wasted work if the blocking concerns are valid.

### Combining Flags

You can combine flags to customize the workflow:

```text
/tiki:yolo 34 --no-tdd --skip-review
/tiki:yolo 34 --force-review --no-tdd
```

This runs the minimal pipeline (5 steps): fetch → plan → audit → execute → review queue.

## Examples

### Example 1: Successful YOLO Execution

```text
User: /tiki:yolo 34

Claude:
## YOLO Mode: Issue #34

Mode: TDD enabled, Review enabled

[1/6] Fetching issue... OK
      Issue #34: Add user authentication
      State: open
      Labels: feature, high-priority

[2/6] Reviewing issue... OK (2 recommendations added)
      - Alternative: Consider using existing auth middleware
      - Concern: No rate limiting mentioned

[3/6] Creating plan... OK
      Phases: 3
      - Phase 1: Setup auth middleware
      - Phase 2: Add login endpoint
      - Phase 3: Add protected routes

[4/6] Auditing plan... OK

[5/6] Executing phases (TDD: enabled)...
      Phase 1/3: Setup auth middleware... DONE
        Tests: 4 passing
      Phase 2/3: Add login endpoint... DONE
        Tests: 5 passing
        DISCOVERED: Consider adding rate limiting
      Phase 3/3: Add protected routes... DONE
        Tests: 3 passing

[6/6] Reviewing queue... 1 item found

### Queue Items Discovered

1. Consider adding rate limiting
   Source: Phase 2
   Type: potential-issue

Actions:
- Create issues from all: `/tiki:review-queue --create-all`
- Review individually: `/tiki:review-queue`

---

## YOLO Complete!

Issue #34: Add user authentication
All 3 phases completed successfully.
TDD: enabled (12 tests passing)
Queue: 1 item pending review

### Phase Summaries
- Phase 1: Created JWT validation middleware with AuthRequest type
- Phase 2: Implemented POST /api/login with password validation
- Phase 3: Applied auth middleware to /api/user routes

### Next Steps
- Review queue items: `/tiki:review-queue`
- Close the issue: `gh issue close 34`
```

### Example 2: YOLO with --no-tdd

```text
User: /tiki:yolo 42 --no-tdd

Claude:
## YOLO Mode: Issue #42

Mode: TDD disabled, Review enabled

[1/6] Fetching issue... OK
      Issue #42: Update API documentation
      State: open
      Labels: docs

[2/6] Reviewing issue... OK (no concerns)
      Issue is well-defined, ready to plan.

[3/6] Creating plan... OK
      Phases: 2
      - Phase 1: Update endpoint documentation
      - Phase 2: Add code examples

[4/6] Auditing plan... OK

[5/6] Executing phases (TDD: disabled)...
      Phase 1/2: Update endpoint documentation... DONE
      Phase 2/2: Add code examples... DONE

[6/6] Reviewing queue... OK (0 items)

---

## YOLO Complete!

Issue #42: Update API documentation
All 2 phases completed successfully.
TDD: disabled
Queue: Empty

### Phase Summaries
- Phase 1: Updated OpenAPI spec with new auth endpoints
- Phase 2: Added curl examples for all endpoints

### Next Steps
- Close the issue: `gh issue close 42`
```

### Example 3: YOLO with --skip-review

```text
User: /tiki:yolo 42 --skip-review

Claude:
## YOLO Mode: Issue #42

Mode: TDD enabled, Review skipped

[1/5] Fetching issue... OK
      Issue #42: Update API documentation
      State: open
      Labels: docs

[2/5] Creating plan... OK
      Phases: 2
      - Phase 1: Update endpoint documentation
      - Phase 2: Add code examples

[3/5] Auditing plan... OK

[4/5] Executing phases (TDD: enabled)...
      Phase 1/2: Update endpoint documentation... DONE
      Phase 2/2: Add code examples... DONE

[5/5] Reviewing queue... OK (0 items)

---

## YOLO Complete!

Issue #42: Update API documentation
All 2 phases completed successfully.
TDD: enabled
Queue: Empty

### Next Steps
- Close the issue: `gh issue close 42`
```

### Example 4: YOLO Blocked by Review

```text
User: /tiki:yolo 34

Claude:
## YOLO Mode: Issue #34

Mode: TDD enabled, Review enabled

[1/6] Fetching issue... OK
      Issue #34: Add user authentication and authorization
      State: open
      Labels: feature

[2/6] Reviewing issue... BLOCKED

### Blocking Concerns Found

1. **[Scope]**: This issue combines authentication AND authorization - these should be separate issues
   - Authentication: login, logout, session management
   - Authorization: roles, permissions, access control

These concerns must be addressed before planning can proceed.

### GitHub Comment
Added comment to issue #34 with blocking concerns.

### Options
- Split the issue and retry with the auth-only issue
- Override and continue: `/tiki:yolo 34 --force-review`
- Skip review: `/tiki:yolo 34 --skip-review`

YOLO mode paused.
```

### Example 5: YOLO with --force-review Override

```text
User: /tiki:yolo 34 --force-review

Claude:
## YOLO Mode: Issue #34

Mode: TDD enabled, Review enabled, Force review override

[1/6] Fetching issue... OK
      Issue #34: Add user authentication and authorization
      State: open
      Labels: feature

[2/6] Reviewing issue... BLOCKED (overridden with --force-review)
      - Blocking: Issue should be split into auth + authz

      Proceeding despite blocking concerns (--force-review)

[3/6] Creating plan... OK
      Phases: 4
      - Phase 1: Setup auth middleware
      - Phase 2: Add login endpoint
      - Phase 3: Add role-based access control
      - Phase 4: Add protected routes

[4/6] Auditing plan... OK

[5/6] Executing phases (TDD: enabled)...
      Phase 1/4: Setup auth middleware... DONE
      Phase 2/4: Add login endpoint... DONE
      Phase 3/4: Add role-based access control... DONE
      Phase 4/4: Add protected routes... DONE

[6/6] Reviewing queue... OK (0 items)

---

## YOLO Complete!

Issue #34: Add user authentication and authorization
All 4 phases completed successfully.
TDD: enabled
Queue: Empty

### Next Steps
- Close the issue: `gh issue close 34`
```

### Example 6: YOLO with Warnings (continues)

```text
User: /tiki:yolo 35

Claude:
## YOLO Mode: Issue #35

Mode: TDD enabled, Review enabled

[1/6] Fetching issue... OK
      Issue #35: Add login endpoint
      State: open
      Labels: feature

[2/6] Reviewing issue... OK (with warnings)
      - Warning: No rate limiting mentioned for login endpoint
      - Warning: Password policy not specified

      Proceeding despite warnings.

[3/6] Creating plan... OK
      Phases: 2
      - Phase 1: Add login route handler
      - Phase 2: Add password validation

[4/6] Auditing plan... OK

[5/6] Executing phases (TDD: enabled)...
      Phase 1/2: Add login route handler... DONE
      Phase 2/2: Add password validation... DONE

[6/6] Reviewing queue... OK (0 items)

---

## YOLO Complete!

Issue #35: Add login endpoint
All 2 phases completed successfully.
TDD: enabled
Queue: Empty

### Next Steps
- Close the issue: `gh issue close 35`
```

### Example 7: YOLO Blocked by Audit

```text
User: /tiki:yolo 15

Claude:
## YOLO Mode: Issue #15

Mode: TDD enabled, Review enabled

[1/6] Fetching issue... OK
      Issue #15: Refactor database layer
      State: open
      Labels: refactor

[2/6] Reviewing issue... OK (1 recommendation added)
      - Concern: Large refactor - consider splitting into smaller issues

[3/6] Creating plan... OK
      Phases: 5
      - Phase 1: Extract connection pool
      - Phase 2: Add query builder
      - Phase 3: Migrate user queries
      - Phase 4: Migrate order queries
      - Phase 5: Update integration tests

[4/6] Auditing plan... BLOCKED

The plan has blocking issues that prevent execution:

Errors:
- Phase 3 depends on Phase 4 which comes later (dependency order invalid)
- Phase 2 references non-existent file: src/db/legacy-pool.ts

Resolution required. Run `/tiki:plan-issue 15` to revise the plan.
```

## Workflow Overview

```text
YOLO Mode Pipeline (6 steps, or 5 with --skip-review):

  [User Input]
       |
       v
  +------------+     +--------------+     +------------+
  | GET-ISSUE  | --> | REVIEW-ISSUE | --> | PLAN-ISSUE |
  +------------+     +--------------+     +------------+
       |                   |                    |
       v                   v                    v
    Fetch             Analyze for          Analyze &
    GitHub            alternatives,        Create
    Issue             concerns,            Phases
                      questions
       |                   |                    |
       +-------------------+--------------------+
                           |
                           v
                     +------------+
                     | AUDIT-PLAN |
                     +------------+
                           |
                           v
                      Validate
                      Dependencies,
                      Files, Sizes
                           |
                           v (if no blocking errors)
                     +------------+
                     |  EXECUTE   |
                     | (with TDD) |
                     +------------+
                           |
                           v
                     +--------------+
                     | REVIEW-QUEUE |
                     +--------------+
                           |
                           v
                       [Complete]
```

## Cleanup

After YOLO completes (success or failure), clean up any temporary artifacts:

```bash
# Remove common temporary artifacts from the project root
rm -f ./tmpclaude-* ./nul ./NUL 2>/dev/null || true

# Also clean up any temp files in .tiki directory
rm -f .tiki/tmp-* .tiki/*.tmp 2>/dev/null || true
```

Run this cleanup silently at the end of the workflow, regardless of outcome.

If artifacts persist, run `/tiki:cleanup` manually.

## Notes

- YOLO mode is designed for confident execution when you trust the workflow
- Each step validates before proceeding to the next
- Progress is saved at each step, so partial failures don't lose work
- TDD is enabled by default to ensure quality - use `--no-tdd` only when appropriate
- If any step fails, the pipeline stops with clear instructions for recovery
- Queue review at the end ensures discovered items aren't forgotten
- State files are updated throughout, so `/tiki:state` shows accurate progress
- For more control over individual steps, use the separate commands:
  - `/tiki:get-issue` - Just fetch and display
  - `/tiki:plan-issue` - Manual planning with more options
  - `/tiki:audit-plan` - Audit with `--verbose` for details
  - `/tiki:execute` - Execute with `--from N` or `--dry-run`
  - `/tiki:review-queue` - Interactive queue management
