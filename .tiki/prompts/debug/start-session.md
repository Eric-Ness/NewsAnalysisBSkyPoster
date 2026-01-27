# Start Debug Session

Conditionally loaded when starting a new debug session (not resume/list/show/search).

## Check Similar Sessions

Before creating a new session, check for related past sessions.

### Load and Score

1. Read `.tiki/debug/index.json` (skip if missing)
2. Extract search terms from issue title or symptom description:
   - Split into words, remove common stop words
   - Include error codes, function names, file paths
3. Score each existing session against extracted terms:

| Match Type | Points |
|------------|--------|
| Keyword in `keywords` | +2 |
| Term in `title` | +3 |
| Term in `rootCause` | +4 |
| Term in `errorPatterns` | +5 |
| Same `issue` number | +10 |

### Display Matches

If any session scores >= 5:

```
Similar sessions found:
| # | Session | Score | Status | Root Cause |
|---|---------|-------|--------|------------|
| 1 | issue-42-auth | 12 | Resolved | Missing token refresh |
| 2 | untracked-api | 7 | Abandoned | - |

Options:
[1-N] View session details
[c] Continue with new session
[r] Resume a listed session
```

### Handle User Choice

- **Number (1-N)**: Read and display that session's debug document, then ask:
  - "Does this session help solve your issue?"
  - If yes: user can apply past solution or resume that session
  - If no: continue with new session creation
- **c (continue)**: Proceed to create new session
- **r (resume)**: Ask which listed session to resume, switch to resume mode

### Skip Conditions

Skip similarity check if:
- No index exists
- Index has < 2 sessions
- User provided `--force` flag

## Create Session Document

### Filename Convention

Generate a descriptive, unique filename:

- **Issue-linked**: `issue-{N}-{kebab-title}.md`
  - Use issue number and 3-5 word summary of the bug
  - Example: `issue-42-auth-token-expired.md`
- **Untracked**: `untracked-{kebab-symptom}.md`
  - Use 3-5 word summary of the symptom
  - Example: `untracked-api-500-errors.md`

Kebab conversion rules:

- Lowercase all characters
- Replace spaces with hyphens
- Remove special characters (keep alphanumeric and hyphens)
- Limit to 5 meaningful words
- Avoid generic words like "bug", "error", "issue" at start

### Document Template

Create `.tiki/debug/{filename}` with:

```markdown
# Debug Session: {Title}

## Session Info

| Field | Value |
|-------|-------|
| Started | {YYYY-MM-DD HH:MM} |
| Issue | #{N} or "Untracked" |
| Status | Active |
| Last Updated | {YYYY-MM-DD HH:MM} |

## Symptoms

{To be filled after gathering}

## Environment

{Auto-detected}

## Hypotheses

{Hypotheses added during investigation}

## Investigation Log

| Time | Action | Result |
|------|--------|--------|

## Root Cause

{Identified when confirmed}

## Solution Applied

{Documented on resolution}

## Lessons Learned

{Captured before closing}
```

## Gather Symptoms

### Initial Questions

Ask the user these 4 questions (wait for responses):

1. **What is failing?** - Specific behavior or error
2. **Error messages?** - Exact error text, stack traces, logs
3. **When did it start?** - After a change? Random? Always?
4. **Reproducible?** - Steps to reproduce, frequency

### Auto-Detect Environment

Run these commands to capture context:

```bash
# Git state
git status --short
git log --oneline -3

# Node/npm (if applicable)
node --version 2>/dev/null
npm --version 2>/dev/null

# Python (if applicable)
python --version 2>/dev/null

# Recent changes
git diff --stat HEAD~3..HEAD 2>/dev/null | tail -10
```

### Document Findings

Update the session file's Symptoms section with:
- User's answers (verbatim quotes for errors)
- Reproduction steps if provided
- Frequency/pattern observations

Update Environment section with:
- Relevant tool versions
- Git branch and recent commits
- Any notable file changes

## Initial Analysis

After gathering symptoms, perform structured analysis:

### 1. Categorize Issue Type

Determine the primary category:

| Type | Indicators |
|------|------------|
| Runtime error | Exceptions, crashes, unexpected output |
| Build failure | Compilation errors, missing dependencies |
| Test failure | Assertions failing, flaky tests |
| Performance | Slowness, timeouts, resource exhaustion |
| Logic bug | Wrong results, incorrect behavior |
| Integration | API failures, connection issues |

### 2. Identify Potential Areas

Based on error messages and symptoms:

- Parse stack traces for file/line references
- Check recently modified files (from git diff)
- Identify affected subsystems/modules
- Note any patterns (timing, specific inputs, environment)

### 3. Generate Initial Hypotheses

Create 2-4 testable hypotheses ranked by likelihood:

- Each hypothesis must be specific (not "something is wrong")
- Each must have a clear test approach
- Consider both obvious and non-obvious causes
- Format: "H{N}: {specific hypothesis} - Test: {concrete approach}"

Example hypotheses:

- "H1: Auth token expires before refresh - Test: Log token timestamps"
- "H2: Race condition in async handler - Test: Add timing logs"
- "H3: Missing null check on API response - Test: Add defensive logging"

### 4. Present to User

Display analysis and await selection:

```text
Initial Analysis:
- Type: {category}
- Likely areas: {files/subsystems}
- Pattern: {any observed pattern}

Suggested hypotheses:
H1: {most likely} - Test: {approach}
H2: {second likely} - Test: {approach}
H3: {alternative} - Test: {approach}

Select hypothesis to investigate [1-N] or describe your own:
```

### 5. Transition to Hypothesis Workflow

Once user selects a hypothesis:

1. Record selection in Investigation Log with timestamp
2. Load `hypothesis-tracking.md` for the test/record workflow
3. Begin systematic testing of the selected hypothesis
