---
type: prompt
name: tiki:plan-issue
description: Break a GitHub issue into executable phases. Use when planning work on an issue, creating a phased implementation plan, or before executing an issue.
allowed-tools: Bash, Read, Write, Glob, Grep
argument-hint: <issue-number> [additional-numbers...]
---

# Plan Issue

Take a GitHub issue and create a phased execution plan. Each phase should be small enough to complete in one context window.

## Usage

```
/tiki:plan-issue 34
/tiki:plan-issue 34 45    # Plan multiple issues together
```

## Instructions

### Step 1: Fetch the Issue

```bash
gh issue view <number> --json number,title,body,state,labels,assignees,milestone
```

### Step 2: Analyze the Issue

Read the issue content and understand:
- What is the goal?
- What files will likely need to change?
- What are the dependencies?
- How complex is this task?

### Step 3: Explore the Codebase (if needed)

If the issue references existing code:
- Use Glob to find relevant files
- Use Grep to understand current implementation
- Read key files to understand context

### Step 4: Break Into Phases

Create phases following these principles:

1. **Each phase must be completable in one context window**
   - A sub-agent will execute each phase with fresh context
   - Phase should be focused and atomic

2. **Phases should be independently verifiable**
   - Include clear verification steps
   - Tests should pass after each phase

3. **Declare dependencies explicitly**
   - If Phase 3 depends on Phase 2, say so
   - Phases without dependencies can potentially run in parallel

4. **Identify files each phase will modify**
   - Helps avoid conflicts
   - If two phases modify the same file, consider splitting differently

### Step 5: Create the Plan File

Create `.tiki/plans/issue-<number>.json` with this structure:

```json
{
  "issue": {
    "number": 34,
    "title": "Issue title from GitHub",
    "url": "https://github.com/owner/repo/issues/34"
  },
  "created": "2026-01-10T10:00:00Z",
  "status": "planned",
  "phases": [
    {
      "number": 1,
      "title": "Short descriptive title",
      "status": "pending",
      "priority": "high|medium|low",
      "dependencies": [],
      "files": ["src/file1.ts", "src/file2.ts"],
      "content": "Detailed instructions for what to do in this phase...",
      "verification": [
        "File exists and exports correct types",
        "No TypeScript errors",
        "Tests pass"
      ],
      "summary": null,
      "completedAt": null
    }
  ],
  "queue": [],
  "metadata": {
    "estimatedPhases": 3,
    "actualPhases": 3,
    "parallelizable": false
  }
}
```

### Step 6: Display the Plan

After creating the plan, display a summary:

```
## Plan for Issue #34: Add user authentication

**Phases:** 3
**Parallelizable:** No

### Phase 1: Setup auth middleware (high priority)
- Files: src/middleware/auth.ts, src/types/auth.ts
- Dependencies: None
- Verification: Middleware exports, no TS errors

### Phase 2: Add login endpoint (high priority)
- Files: src/routes/auth.ts, src/services/auth.ts
- Dependencies: Phase 1
- Verification: POST /api/login works, tests pass

### Phase 3: Add protected routes (medium priority)
- Files: src/routes/user.ts
- Dependencies: Phase 1, 2
- Verification: 401 without auth, 200 with auth

---
Plan saved to `.tiki/plans/issue-34.json`

Ready to execute? Use `/tiki:execute 34`
Want to adjust phases? Use `/tiki:discuss-phases 34`
```

## Phase Content Guidelines

The `content` field for each phase should include:

1. **Clear objective** - What this phase accomplishes
2. **Specific tasks** - Step-by-step what to do
3. **Context from previous phases** - What to build on (if applicable)
4. **Code patterns to follow** - Reference existing code style
5. **Edge cases to handle** - Anything tricky to watch for

Example phase content:
```
Create the authentication middleware that validates JWT tokens.

Tasks:
1. Create src/middleware/auth.ts
2. Implement validateToken() function that:
   - Extracts token from Authorization header
   - Verifies JWT signature using jsonwebtoken
   - Attaches decoded user to request object
3. Create src/types/auth.ts with AuthRequest interface
4. Export middleware for use in routes

Follow the existing middleware pattern in src/middleware/logger.ts.

Edge cases:
- Missing Authorization header → 401
- Invalid token format → 401
- Expired token → 401 with specific message
```

## Handling Simple vs Complex Issues

### Simple Issue (1 phase)
If the issue is small enough for one context window, create a single phase:
```json
{
  "phases": [
    {
      "number": 1,
      "title": "Complete implementation",
      "content": "Full implementation details...",
      ...
    }
  ],
  "metadata": {
    "estimatedPhases": 1,
    "actualPhases": 1,
    "parallelizable": false
  }
}
```

### Complex Issue (multiple phases)
Break into logical chunks:
- By component (auth middleware → login endpoint → protected routes)
- By layer (database → service → API → tests)
- By file (if a large file needs multiple changes)

## Error Handling

- **Issue not found:** "Issue #<number> not found. Check the issue number."
- **Issue already planned:** "Plan already exists at `.tiki/plans/issue-<number>.json`. Use `/tiki:discuss-phases` to modify or delete the file to re-plan."
- **No gh CLI:** "GitHub CLI (gh) not installed or not authenticated."

## Notes

- Plans are stored in `.tiki/plans/` directory
- Status values: `planned`, `in_progress`, `completed`, `failed`
- Phase status values: `pending`, `in_progress`, `completed`, `failed`, `skipped`
- Always suggest `/tiki:execute` as the next step after planning
