---
type: prompt
name: tiki:review-issue
description: Review a GitHub issue before planning. Provides a "think twice" step to identify alternatives, concerns, and clarifying questions.
allowed-tools: Bash, Read, Glob, Grep
argument-hint: <issue-number> [--quiet] [--edit-body] [--yolo]
---

# Review Issue

A pre-planning review step that gives you a chance to re-read the GitHub issue, consider alternatives, identify concerns, and enrich the issue with recommendations before committing to a plan.

## Usage

```text
/tiki:review-issue 34
/tiki:review-issue 34 --quiet          # Don't add comment if no concerns
/tiki:review-issue 34 --edit-body      # Edit issue body instead of comment (not recommended)
/tiki:review-issue 34 --yolo           # Return structured verdict for YOLO mode integration
```

## Instructions

### Step 1: Parse Arguments

```javascript
const issueNumber = args[0];  // Required
const quiet = args.includes('--quiet');
const editBody = args.includes('--edit-body');
const yoloMode = args.includes('--yolo');
```

If no issue number provided:
```text
Review requires an issue number.

Usage: /tiki:review-issue <issue-number> [--quiet] [--edit-body]

Example: /tiki:review-issue 34
```

### Step 2: Fetch the Issue

```bash
gh issue view <number> --json number,title,body,state,labels,comments
```

**If issue not found:**
```text
Issue #<number> not found.

Verify the issue number and try again.
```

### Step 3: Analyze the Issue

When reviewing this issue, think critically about:

1. **ALTERNATIVES**: Are there simpler or more standard ways to accomplish this?
   - Existing libraries that could help?
   - Patterns already in the codebase to reuse?
   - Different architectural approaches?

2. **ASSUMPTIONS**: What is being assumed about the codebase, environment, or requirements?
   - What's not explicitly stated but implied?
   - Are there hidden dependencies?

3. **BLOCKERS**: What could prevent this from being completed?
   - Dependencies on other work?
   - Required permissions or access?
   - External services or APIs?

4. **EDGE CASES**: What scenarios might cause problems?
   - Error handling needs?
   - Empty states?
   - Concurrent access?
   - Rate limiting?

5. **SCOPE**: Is this well-scoped?
   - Should it be split into multiple issues?
   - Is it trying to do too much?
   - Are there parts that could be deferred?

6. **CLARITY**: Is the acceptance criteria clear and testable?
   - How will we know when it's done?
   - Are requirements specific enough?
   - Any ambiguous terms?

7. **RISKS**: Any performance, security, or compatibility concerns?
   - Database migrations?
   - Breaking changes?
   - Security implications?

8. **PRIOR ART**: Does similar functionality exist that should be reused or referenced?
   - Similar features in the codebase?
   - Related issues or PRs?

**Important:** Focus on surfacing concerns and clarifications, NOT expanding scope. The goal is to validate the existing issue, not add features.

### Step 4: Explore Codebase (if needed)

If the issue references existing code or functionality:
- Use Glob to find relevant files
- Use Grep to understand current implementation
- Read key files to understand context

This helps identify:
- Whether similar functionality already exists
- Patterns to follow or avoid
- Potential conflicts with existing code

### Step 5: Compile Findings

Categorize your findings by **severity level**:

#### Severity Levels

| Severity | Description | YOLO Behavior |
|----------|-------------|---------------|
| **blocking** | Cannot proceed without resolution | PAUSE and ask user |
| **warning** | Should be addressed but can proceed | Continue with note |
| **info** | FYI, nice to know | Continue silently |

#### Blocking Triggers (use severity: blocking)

| Trigger | Rationale |
|---------|-----------|
| Scope too large / should be split | Will create a bad plan with too many phases |
| Missing dependency on another issue | Work will be blocked anyway |
| Fundamentally wrong approach | Don't waste time planning the wrong thing |
| Critical missing information | Can't plan without it |
| Security vulnerability in proposed approach | Must address before implementation |

#### Warning Triggers (use severity: warning)

| Trigger | Rationale |
|---------|-----------|
| Missing edge case handling | Can be added during implementation |
| Performance concerns | Important but not blocking |
| Missing tests mentioned | TDD mode will handle this |
| Rate limiting not specified | Should be added, but doesn't block |
| Alternative approach exists | Nice to know, not blocking |

#### Info Triggers (use severity: info)

| Trigger | Rationale |
|---------|-----------|
| Prior art exists in codebase | Reference for implementation |
| Alternative library available | Option to consider |
| Nice-to-have additions | Future enhancement ideas |

#### Structure Findings As:

1. **Blocking Concerns** (if any)
   - Issues that MUST be resolved before planning
   - Mark with category: scope, dependency, approach, missing_info, security

2. **Warnings** (if any)
   - Issues that SHOULD be addressed but don't block
   - Mark with category: edge_case, performance, testing, rate_limiting

3. **Info** (if any)
   - FYI items that are good to know
   - Mark with category: prior_art, alternative, enhancement

4. **Alternative Approaches** (if any)
   - Different ways to solve the problem
   - Trade-offs of each approach

5. **Clarifying Questions** (if any)
   - Ambiguities that need resolution
   - Missing information

#### Determine Verdict

Based on findings, set the verdict:
- **blocked**: Has at least one blocking concern
- **warnings**: No blocking concerns, but has warnings
- **clean**: No blocking concerns or warnings (may have info items)

### Step 6: Add GitHub Comment (if findings exist)

**If there are findings to share** (and not using `--edit-body`):

```bash
gh issue comment <number> --body "## Pre-Planning Review

Reviewed by Claude before planning. Here are some considerations:

### Blocking Concerns
- **[Category]**: <concern description>

### Warnings
- **[Category]**: <warning description>

### Info
- **[Category]**: <info description>

### Alternative Approaches
- <alternative 1>
- <alternative 2>

### Clarifying Questions
- <question 1>

### Verdict: <BLOCKED | WARNINGS | CLEAN>

---
*This review was generated by \`/tiki:review-issue\`. Proceed with \`/tiki:plan-issue <number>\` when ready.*"
```

Only include sections that have content. Skip empty sections.

**If using `--edit-body`** (not recommended):
Instead of adding a comment, prepend the review to the issue body. This modifies the original issue, which may not be desired.

**If no concerns found:**
- Default behavior: Stay silent (no comment added)
- With `--quiet` flag: Same behavior
- Without findings, just report to user that the issue looks good

### Step 7: Display Summary to User

Always display a summary of the review with severity-based categorization:

**If verdict is "blocked":**

```text
## Issue Review: #<number>

### Blocking Concerns (<N>)
- **[Scope]**: This issue should be split - <reason>
- **[Dependency]**: Missing dependency on issue #<N>

### Warnings (<N>)
- **[Edge Case]**: <warning description>

### Info (<N>)
- **[Prior Art]**: Similar pattern exists in <file>

### Verdict: BLOCKED
Cannot proceed to planning without addressing blocking concerns.

### GitHub Comment
Added comment to issue #<number> with blocking concerns.

### Next Steps
- Address the blocking concerns listed above
- When resolved: `/tiki:review-issue <number>` to re-review
```

**If verdict is "warnings":**

```text
## Issue Review: #<number>

### Warnings (<N>)
- **[Edge Case]**: <warning description>
- **[Performance]**: <warning description>

### Info (<N>)
- **[Prior Art]**: Similar pattern exists in <file>

### Verdict: WARNINGS
No blocking concerns. May proceed with caution.

### GitHub Comment
Added comment to issue #<number> with recommendations.

### Next Steps
- Consider addressing the warnings
- Ready to proceed: `/tiki:plan-issue <number>`
```

**If verdict is "clean":**

```text
## Issue Review: #<number>

### Findings
No significant concerns identified. The issue appears well-defined.

### Verdict: CLEAN

### GitHub Comment
No comment added - issue looks ready to plan.

### Next Steps
- Ready to proceed: `/tiki:plan-issue <number>`
```

### Step 8: Return Structured Result (for YOLO mode)

**If `--yolo` flag is present**, also output a structured result block that YOLO can parse:

```text
<!-- REVIEW_RESULT
{
  "blocking": [
    { "category": "scope", "message": "Issue should be split..." }
  ],
  "warnings": [
    { "category": "edge_case", "message": "No rate limiting..." }
  ],
  "info": [
    { "category": "prior_art", "message": "Similar pattern exists..." }
  ],
  "verdict": "blocked"
}
REVIEW_RESULT -->
```

The verdict field will be one of: `"blocked"`, `"warnings"`, or `"clean"`.

This structured output allows YOLO mode to programmatically determine whether to continue or pause execution.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Comment vs edit body | **Comment** | Preserves original intent, shows review as distinct step |
| Silent when no concerns | **Yes (default)** | Reduces noise on simple issues |
| Scope recommendations | **Clarify, don't expand** | Avoid feature creep; focus on concerns not additions |

## Examples

### Example 1: Issue with Blocking Concerns

```text
User: /tiki:review-issue 34

Claude:
## Issue Review: #34

### Blocking Concerns (1)
- **[Scope]**: This issue combines authentication AND authorization - these should be separate issues
  - Authentication: login, logout, session management
  - Authorization: roles, permissions, access control

### Warnings (2)
- **[Edge Case]**: No rate limiting mentioned for login endpoint
- **[Security]**: Password policy not specified

### Info (1)
- **[Prior Art]**: Similar auth pattern exists in `src/middleware/session.ts`

### Verdict: BLOCKED
Cannot proceed to planning without addressing blocking concerns.

### GitHub Comment
Added comment to issue #34 with blocking concerns.

### Next Steps
- Split the issue into separate auth and authz issues
- When resolved: `/tiki:review-issue 34` to re-review
```

### Example 2: Issue with Warnings Only

```text
User: /tiki:review-issue 35

Claude:
## Issue Review: #35

### Warnings (2)
- **[Edge Case]**: No rate limiting mentioned for login endpoint
- **[Performance]**: Consider caching user lookup results

### Info (1)
- **[Prior Art]**: Similar auth pattern exists in `src/middleware/session.ts`

### Verdict: WARNINGS
No blocking concerns. May proceed with caution.

### GitHub Comment
Added comment to issue #35 with recommendations.

### Next Steps
- Consider addressing the warnings
- Ready to proceed: `/tiki:plan-issue 35`
```

### Example 3: Well-Defined Issue (Clean)

```text
User: /tiki:review-issue 42

Claude:
## Issue Review: #42

### Findings
No significant concerns identified. The issue appears well-defined.

- Acceptance criteria is clear
- Scope is appropriate
- No obvious blockers

### Verdict: CLEAN

### GitHub Comment
No comment added - issue looks ready to plan.

### Next Steps
- Ready to proceed: `/tiki:plan-issue 42`
```

### Example 4: Using --quiet Flag

```text
User: /tiki:review-issue 42 --quiet

Claude:
## Issue Review: #42

### Verdict: CLEAN

### Next Steps
- Ready to proceed: `/tiki:plan-issue 42`
```

### Example 5: YOLO Mode Integration

```text
User: /tiki:review-issue 34 --yolo

Claude:
## Issue Review: #34

### Blocking Concerns (1)
- **[Scope]**: This issue should be split...

### Verdict: BLOCKED

### GitHub Comment
Added comment to issue #34 with blocking concerns.

<!-- REVIEW_RESULT
{
  "blocking": [
    { "category": "scope", "message": "This issue should be split - authentication and authorization are separate concerns" }
  ],
  "warnings": [],
  "info": [],
  "verdict": "blocked"
}
REVIEW_RESULT -->
```

## Error Handling

- **Issue not found:** "Issue #<number> not found. Check the issue number and try again."
- **No gh CLI:** "GitHub CLI (gh) is not installed or not authenticated. Run `gh auth login` first."
- **No repo context:** "Not in a git repository or no remote configured."
- **Comment failed:** "Failed to add comment to issue. Check permissions and try again."

## Notes

- This skill is designed as a "think twice" step before planning
- It should NOT expand scope or add new requirements
- Focus is on identifying risks, alternatives, and clarifications
- Run this before `/tiki:plan-issue` for complex or unclear issues
- For simple, well-defined issues, this step may report no concerns
- The GitHub comment serves as a record of the pre-planning analysis
