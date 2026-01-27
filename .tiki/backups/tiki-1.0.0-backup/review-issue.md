---
type: prompt
name: tiki:review-issue
description: Review a GitHub issue before planning. Provides a "think twice" step to identify alternatives, concerns, and clarifying questions.
allowed-tools: Bash, Read, Glob, Grep
argument-hint: <issue-number> [--quiet] [--edit-body] [--yolo]
---

# Review Issue

Pre-planning review to identify alternatives, concerns, and clarifying questions before committing to a plan.

## Usage

```text
/tiki:review-issue 34
/tiki:review-issue 34 --quiet     # Silent if no concerns
/tiki:review-issue 34 --edit-body # Edit issue body (not recommended)
/tiki:review-issue 34 --yolo      # Structured output for YOLO mode
```

## Instructions

### Step 1: Parse Arguments

Parse: `issueNumber` (required), `--quiet`, `--edit-body`, `--yolo` flags.

If no issue number: show usage message and exit.

### Step 2: Fetch Issue

```bash
gh issue view <number> --json number,title,body,state,labels,comments
```

If not found, report error and exit.

### Step 3: Analyze Issue (8 Categories)

Review critically across these categories:

1. **ALTERNATIVES**: Simpler approaches? Existing libraries/patterns to reuse?
2. **ASSUMPTIONS**: What's implied but not stated? Hidden dependencies?
3. **BLOCKERS**: Dependencies on other work? Required permissions/access?
4. **EDGE CASES**: Error handling? Empty states? Concurrency? Rate limiting?
5. **SCOPE**: Well-scoped? Should be split? Parts to defer?
6. **CLARITY**: Clear acceptance criteria? Testable requirements?
7. **RISKS**: Performance, security, compatibility concerns? Breaking changes?
8. **PRIOR ART**: Similar functionality exists? Related issues/PRs?

**Focus on concerns, NOT expanding scope.**

### Step 3.5: Extract Assumptions

Make implicit assumptions explicit. Each assumption has:

- `id`: Unique identifier (assumption-N)
- `confidence`: high | medium | low
- `description`: What is being assumed
- `source`: Where assumption comes from

**Confidence levels:**

- **high**: Following established codebase patterns -> proceed confidently
- **medium**: Reasonable defaults -> note but proceed
- **low**: Needs clarification -> surface as info-level finding

**Extraction workflow:**

1. Scan issue for implicit language ("should just", "like existing", "use the")
2. Check for technical assumptions (database, API, auth, migration mentions)
3. After Step 4, add pattern-based assumptions from codebase
4. Deduplicate and sort by confidence (low first)
5. Low-confidence assumptions -> info-level findings

### Step 4: Explore Codebase

If issue references existing code:

- Use Glob to find relevant files
- Use Grep to understand implementation
- Identify similar functionality, patterns, potential conflicts

### Step 4.5: Check Research Coverage

Extract technology mentions from issue. Compare against:

- `.tiki/STACK.md` (familiar technologies from `/tiki:map-codebase`)
- `.tiki/research/index.json` (previously researched topics)

Unfamiliar topics -> info-level research suggestions.

### Step 4.7: Knowledge Context (Conditional)

**Skip if:** `.tiki/knowledge/index.json` doesn't exist.

Check for related institutional knowledge:

1. Read `.tiki/prompts/review-issue/knowledge-context.md`
2. Follow knowledge matching workflow
3. Add matches as info-level findings in **PRIOR ART** category

### Step 5: Compile Findings

Categorize by severity:

| Severity | Description | YOLO Behavior |
|----------|-------------|---------------|
| **blocking** | Cannot proceed without resolution | PAUSE and ask user |
| **warning** | Should be addressed but can proceed | Continue with note |
| **info** | FYI, nice to know | Continue silently |

**Blocking triggers:** Scope too large, missing dependencies, wrong approach, critical missing info, security vulnerabilities.

**Warning triggers:** Missing edge cases, performance concerns, rate limiting not specified.

**Info triggers:** Prior art exists, alternatives available, unfamiliar topics detected.

**Determine verdict:**

- `blocked`: Has blocking concerns
- `warnings`: No blocking, but has warnings
- `clean`: No blocking or warnings

### Conditional Analysis Loading

Based on initial findings, load additional analysis as needed:

1. **If risks or security concerns identified:**
   - Read `.tiki/prompts/review-issue/risk-assessment.md`
   - Apply risk assessment workflow

2. **If --alternatives flag or complex issue:**
   - Read `.tiki/prompts/review-issue/alternative-analysis.md`
   - Evaluate alternative approaches

3. **If blocking concerns found:**
   - Read `.tiki/prompts/review-issue/blocking-concerns.md`
   - Apply blocking concern handling

### Step 6: Add GitHub Comment

**If findings exist** (and not `--edit-body`):

```bash
gh issue comment <number> --body "## Pre-Planning Review

### Blocking Concerns
- **[Category]**: <description>

### Warnings
- **[Category]**: <description>

### Info
- **[Category]**: <description>

### Assumptions
**High Confidence**: <description> _(source)_
**Medium Confidence**: <description> _(source)_
**Low Confidence**: <description> _(source)_

### Alternative Approaches
- <alternative>

### Clarifying Questions
- <question>

### Verdict: <BLOCKED | WARNINGS | CLEAN>

---
*Generated by \`/tiki:review-issue\`. Proceed with \`/tiki:plan-issue <number>\` when ready.*"
```

Only include sections with content. Skip empty sections.

**If no concerns:** Stay silent (no comment). With `--quiet`: same behavior.

### Step 7: Display Summary

Show severity-categorized summary:

**BLOCKED verdict:**

```text
## Issue Review: #<number>
### Blocking Concerns (<N>)
### Warnings (<N>)
### Info (<N>)
### Verdict: BLOCKED
Cannot proceed without addressing blocking concerns.
### Next Steps
- Address blocking concerns, then re-review
```

**WARNINGS verdict:**

```text
## Issue Review: #<number>
### Warnings (<N>)
### Info (<N>)
### Verdict: WARNINGS
May proceed with caution.
### Next Steps
- Consider addressing warnings
- Ready: `/tiki:plan-issue <number>`
```

**CLEAN verdict:**

```text
## Issue Review: #<number>
### Findings
No significant concerns. Issue well-defined.
### Verdict: CLEAN
### Next Steps
- Ready: `/tiki:plan-issue <number>`
```

### Step 8: YOLO Mode Output

If `--yolo` flag, output structured result:

```text
<!-- REVIEW_RESULT
{
  "blocking": [{ "category": "...", "message": "..." }],
  "warnings": [{ "category": "...", "message": "..." }],
  "info": [{ "category": "...", "message": "...", "topic": "..." }],
  "assumptions": [{ "id": "...", "confidence": "...", "description": "...", "source": "..." }],
  "verdict": "blocked|warnings|clean"
}
REVIEW_RESULT -->
```

### Step 9: Offer Next Steps

Skip if: `workflow.showNextStepMenu` is false in config, `--yolo` flag set, or verdict is BLOCKED.

For CLEAN/WARNINGS, use AskUserQuestion with options:

- "Plan issue (Recommended)" -> invoke `tiki:plan-issue`
- "Research" -> invoke `tiki:research`
- "Done for now" -> exit

## Error Handling

- **Issue not found:** Report error with issue number
- **No gh CLI:** Prompt to run `gh auth login`
- **No repo context:** Report not in git repository
- **Comment failed:** Report permission issue
