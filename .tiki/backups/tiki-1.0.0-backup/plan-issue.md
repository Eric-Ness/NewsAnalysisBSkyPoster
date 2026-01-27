---
type: prompt
name: tiki:plan-issue
description: Break a GitHub issue into executable phases. Use when planning work on an issue, creating a phased implementation plan, or before executing an issue.
allowed-tools: Bash, Read, Write, Glob, Grep
argument-hint: <issue-number> [additional-numbers...] [--no-research] [--no-project]
---

# Plan Issue

Take a GitHub issue and create a phased execution plan. Each phase should be small enough to complete in one context window.

## Usage

```text
/tiki:plan-issue 34
/tiki:plan-issue 34 45    # Plan multiple issues together
/tiki:plan-issue 34 --no-research  # Skip research integration
/tiki:plan-issue 34 --no-project   # Skip PROJECT.md context loading
```

## Instructions

### Step 1: Fetch the Issue

```bash
gh issue view <number> --json number,title,body,state,labels,assignees,milestone
```

### Step 1.5: Load Project Context (Conditional)

**Skip if `--no-project` flag is provided.**

Check if `PROJECT.md` exists in the project root. If found, extract:
- Vision and goals (aligns phases with project objectives)
- Technical constraints (informs architecture decisions)
- Tech stack preferences (guides implementation choices)
- Patterns and conventions (ensures consistency)

Store for use in phase generation. Display briefly:

```text
## Project Context Detected

**Project:** {Name}
**Vision:** {First line}

Constraints: {list key constraints}
Tech stack: {language} / {framework} / {database}
```

If PROJECT.md not found, skip silently. For greenfield projects without existing code, suggest `/tiki:new-project`.

### Step 2: Analyze the Issue

Read the issue content and understand:
- What is the goal?
- What files will likely need to change?
- What are the dependencies?
- How complex is this task?

### Step 2.25: Research Integration (Conditional)

**Skip if `--no-research` flag is provided.**

Check if `.tiki/research/index.json` exists. If research integration is needed:
- Read `.tiki/prompts/plan-issue/research-integration.md`
- Follow the research matching and extraction workflow
- Store research context for use in phase generation

### Step 2.3: Release Integration (Conditional)

Check if this issue is part of any active release by scanning `.tiki/releases/*.json`.

If issue found in a release:
- Read `.tiki/prompts/plan-issue/release-integration.md`
- Follow the release detection and requirements mapping workflow
- Store release context for use in phase generation and display

**Error handling:** If release detection fails, skip silently and continue normal planning.

### Step 2.35: Knowledge Retrieval (Conditional)

**Skip if `.tiki/knowledge/index.json` doesn't exist.**

Check if knowledge entries exist:

- Read `.tiki/prompts/plan-issue/knowledge-retrieval.md`
- Follow the knowledge matching and display workflow
- Store matched entries for reference in phases

### Step 2.4: Import or Generate Assumptions (Conditional)

Check issue comments for prior review results (look for `REVIEW_RESULT:` marker).

If no prior review assumptions found:
- Read `.tiki/prompts/plan-issue/assumption-generation.md`
- Generate assumptions based on issue and codebase analysis

Store assumptions for mapping to phases in Step 4.5.

### Step 2.5: Extract Success Criteria

Extract and define success criteria that will guide implementation and verify completion.

#### Parse Explicit Criteria

Look for "Acceptance Criteria" sections in the issue body:
- Markdown checkboxes (`- [ ]` items)
- Numbered lists under "Acceptance Criteria" or "Requirements" headers
- Definition of Done sections

#### Generate Implicit Criteria

Analyze the issue to generate additional criteria for:
- **Non-functional**: Performance, security, accessibility, maintainability
- **Testing**: Unit tests, integration tests, edge cases to cover
- **Edge cases**: Error handling, boundary conditions, invalid inputs

#### Categorize All Criteria

1. **Functional**: Core behavior and feature requirements
2. **Non-functional**: Performance, security, scalability attributes
3. **Testing**: Required test coverage and verification
4. **Documentation**: README, API docs, code comments

Optionally confirm with user: `Proceed with these criteria? [y/edit/add more]`

### Step 3: Explore the Codebase

If the issue references existing code:
- Use Glob to find relevant files
- Use Grep to understand current implementation
- Read key files to understand context

### Step 4: Break Into Phases (Backward Planning)

**Critical: Use criteria-driven backward planning, not forward planning from issue description.**

#### Backward Planning Workflow

1. **Start from criteria** - For each criterion, ask: "What code changes make it true?"
   - `functional-1: User can log in` -> login endpoint, session handling, password validation
   - `testing-1: Unit tests for auth` -> test files, mocks, test cases

2. **Derive changes** - For each criterion, identify specific code changes needed

3. **Group into phases** - Combine related changes that:
   - Touch the same files or components
   - Have natural dependencies on each other
   - Can be verified together

4. **Ensure criterion justification** - Every phase exists because specific criteria require it

#### Phase Generation Principles

1. **Completable in one context window** - Each phase runs as a sub-agent with fresh context
2. **Independently verifiable** - Include clear verification steps; tests should pass after each phase
3. **Explicit dependencies** - If Phase 3 depends on Phase 2, declare it
4. **Identify files modified** - Helps avoid conflicts between phases
5. **Map to success criteria** - Use `addressesCriteria` field (e.g., `"functional-1"`, `"testing-2"`)

#### Incorporating Context

When project context is available (Step 1.5):
- Align phases with project goals
- Respect technical constraints
- Apply tech stack preferences
- Follow documented patterns

When research context is available (Step 2.25):
- Reference research recommendations in phase content
- Add `researchReferences` field to phases
- Note stale research (>30 days) with refresh warning

### Step 4.5: Map Assumptions to Phases

After generating phases, map each assumption to the phases it affects:

1. **Analyze relationships** - Match assumption content against phase titles and content
2. **Populate `affectsPhases`** - List phase numbers affected by each assumption
3. **Detect orphans** - Warn if assumptions don't map to any phase (may be global assumptions)

### Step 5: Create the Plan File

Create `.tiki/plans/issue-<number>.json`. Schema reference: `.tiki/schemas/plan.schema.json`

#### Plan Structure

```json
{
  "issue": { "number": 34, "title": "Issue title", "url": "..." },
  "created": "ISO timestamp",
  "status": "planned",
  "successCriteria": [
    { "category": "functional", "description": "..." },
    { "category": "non-functional", "description": "..." },
    { "category": "testing", "description": "..." },
    { "category": "documentation", "description": "..." }
  ],
  "assumptions": [
    { "id": "A1", "confidence": "high|medium|low", "description": "...", "source": "...", "affectsPhases": [1, 2] }
  ],
  "phases": [
    {
      "number": 1,
      "title": "Phase title",
      "status": "pending",
      "priority": "high|medium|low",
      "addressesCriteria": ["functional-1", "testing-1"],
      "researchReferences": ["topic-name"],
      "dependencies": [],
      "files": ["src/file.ts"],
      "content": "Detailed phase instructions...",
      "subtasks": [],
      "verification": ["Check 1", "Check 2"],
      "summary": null,
      "completedAt": null
    }
  ],
  "researchContext": { "matched": [], "keywords": [], "staleWarnings": [] },
  "projectContext": { "name": "...", "hasProject": true, "constraintsApplied": [], "techStackUsed": [] },
  "coverageMatrix": { "functional-1": { "phases": [1, 2] }, "testing-1": { "phases": [1] } },
  "addressesRequirements": [],
  "release": { "version": null, "milestone": null },
  "queue": [],
  "metadata": { "estimatedPhases": 3, "actualPhases": 3, "parallelizable": false }
}
```

#### Subtasks (Optional)

Phases may include a `subtasks` array for finer-grained parallel execution. Each subtask has:
- `id`: Unique within phase (e.g., "1a", "1b")
- `title`: Short description
- `content`: Detailed instructions
- `dependencies`: Other subtask IDs (within same phase)
- `files`: Files this subtask modifies

Use subtasks when multiple independent pieces can run in parallel. Skip for simple sequential phases.

### Step 5.5: Verify Criteria Coverage

After generating phases, verify all success criteria are addressed:

1. **Build coverage matrix** - Scan all phases' `addressesCriteria` arrays
2. **Detect gaps** - Identify criteria with no associated phases
3. **Warn on uncovered** - Display warning for any missing coverage

```text
**Warning:** The following criteria are not covered by any phase:
- functional-3: User can reset password via email
- testing-2: Integration tests for API endpoints

Consider adding a phase or reviewing the plan.
```

### Step 5.7: Requirements Mapping (Conditional)

**Skip if issue is not in a release or requirements are not enabled.**

If release integration was loaded in Step 2.3, follow the requirements mapping workflow from `.tiki/prompts/plan-issue/release-integration.md`.

### Step 6: Display the Plan

Display a summary showing all available context:

```markdown
## Plan for Issue #34: {title}

**Phases:** {count}
**Parallelizable:** {Yes|No}

### Release Context (if applicable)
**Release:** {version}
**Milestone:** {link or "None"}
**Requirements Addressed:** {list or "None mapped"}

---

### Project Context (if applicable)
**Project:** {name}
**Vision:** {first line}
Constraints: {list}
Tech stack: {stack}

---

### Research Context (if applicable)
Relevant research:
- **{topic}** ({age}) - [View](.tiki/research/{topic}/research.md)

Key recommendations:
- {highlights}
- Avoid: {pitfalls}

{If stale: "Warning: Research over 30 days old. Consider `/tiki:research {topic} --refresh`"}

---

### Knowledge Context (if applicable)

Relevant past work:
- **{title}** ({id}) - from Issue #{ref}
- **{title}** ({id}) - from Issue #{ref}

---

### Assumptions (if applicable)
*{Imported from prior review | Generated during planning}*

**High Confidence:**
- {A1}: {description} - affects Phase {phases}

**Medium/Low Confidence:**
- {A2}: {description} - affects Phase {phases}

---

### Success Criteria

**Functional:**
1. {criterion}

**Non-functional:**
1. {criterion}

**Testing:**
1. {criterion}

**Documentation:**
1. {criterion}

### Phase 1: {title} ({priority} priority)
- Files: {list}
- Dependencies: {list or "None"}
- Addresses Criteria: {list}
- Research: {references if any}
- Verification: {checks}

### Phase N: ...

### Criteria Coverage

**Coverage: {covered}/{total} criteria covered ({percent}%)**

| Criterion | Phases |
|-----------|--------|
| functional-1 | Phase 1, 2 |
| ... | ... |

---
Plan saved to `.tiki/plans/issue-{number}.json`
```

**Display Rules:**

- Omit sections that don't apply (no release, no research, no knowledge, no assumptions)
- Include release context at top if applicable
- Show stale research warnings prominently
- Show knowledge context with source issue references
- Group assumptions by confidence level

### Step 7: Offer Next Steps

Check `.tiki/config.json` for `workflow.showNextStepMenu`. If false, skip.

On success, present options:
- "Audit plan (Recommended)" -> `/tiki:audit-plan`
- "Discuss phases" -> `/tiki:discuss-phases`
- "Execute" -> `/tiki:execute`
- "Done for now" -> exit

Do not show menu if planning failed.

## Phase Content Guidelines

Each phase's `content` field should include:

1. **Clear objective** - What this phase accomplishes
2. **Specific tasks** - Step-by-step instructions
3. **Context from previous phases** - What to build on
4. **Code patterns to follow** - Reference existing style
5. **Edge cases to handle** - Tricky scenarios
6. **Research recommendations** (if applicable)

Example:
```text
Create the authentication middleware that validates JWT tokens.

Tasks:
1. Create src/middleware/auth.ts
2. Implement validateToken() function:
   - Extract token from Authorization header
   - Verify JWT signature
   - Attach decoded user to request
3. Create src/types/auth.ts with AuthRequest interface
4. Export middleware for use in routes

Follow existing pattern in src/middleware/logger.ts.

Edge cases:
- Missing Authorization header -> 401
- Invalid token format -> 401
- Expired token -> 401 with specific message

**Research Reference:** {topic} (if applicable)
**From research - Avoid:** {pitfalls}
```

## Handling Simple vs Complex Issues

### Simple Issue (1 phase)
If small enough for one context window, create a single phase with complete implementation details.

### Complex Issue (multiple phases)
Break into logical chunks:
- By component (auth middleware -> login endpoint -> protected routes)
- By layer (database -> service -> API -> tests)
- By file (if large file needs multiple changes)

## Error Handling

- **Issue not found:** "Issue #<number> not found. Check the issue number."
- **Plan exists:** "Plan exists at `.tiki/plans/issue-<number>.json`. Use `/tiki:discuss-phases` to modify or delete to re-plan."
- **No gh CLI:** "GitHub CLI (gh) not installed or not authenticated."

## Notes

- Plans stored in `.tiki/plans/` directory
- Plan status values: `planned`, `in_progress`, `completed`, `failed`
- Phase status values: `pending`, `in_progress`, `completed`, `failed`, `skipped`
- Research integration matches keywords against `.tiki/research/index.json`
- Research older than 30 days is marked stale with refresh warning
- Conditional prompts in `.tiki/prompts/plan-issue/`:
  - `research-integration.md` - Research matching and extraction
  - `release-integration.md` - Release detection and requirements mapping
  - `assumption-generation.md` - Assumption generation when no prior review
  - `knowledge-retrieval.md` - Knowledge matching and display
