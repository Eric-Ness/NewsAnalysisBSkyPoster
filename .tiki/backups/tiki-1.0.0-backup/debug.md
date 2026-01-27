---
type: prompt
name: tiki:debug
description: Start systematic debugging session with hypothesis tracking. Use when investigating bugs, failures, or unexpected behavior.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
argument-hint: [issue-number | "symptom description"] [--resume] | list | show <name> | --search "query"
---

# Debug

Start a systematic debugging session with hypothesis tracking and solution documentation.

## Usage

```text
/tiki:debug                    # Debug active issue
/tiki:debug 42                 # Debug specific issue
/tiki:debug "API 500 error"    # Debug untracked symptom
/tiki:debug --resume           # Resume existing session
/tiki:debug list               # List all sessions
/tiki:debug show <session>     # Show session details
/tiki:debug --search "query"   # Search past sessions
```

## Instructions

### Step 1: Parse Arguments and Route

| Input | Mode | Action |
|-------|------|--------|
| (none) | Active Issue | Read `.tiki/state/current.json` for `activeIssue` |
| `N` or `#N` | Specific Issue | Debug issue N |
| `"text"` | Untracked | Debug symptom without linked issue |
| `--resume` | Resume | Continue existing session |
| `list` | List | Show all sessions (inline) |
| `show <name>` | Show | Display session details (inline) |
| `--search "q"` | Search | Search history (inline) |

### Step 2: List Mode (inline)

Find sessions in `.tiki/debug/`:

```bash
ls .tiki/debug/*.md 2>/dev/null | head -20
```

Display by status (Active/Resolved/Abandoned). Parse Session Info table from each file for status/dates.

Format: `| Session | Issue | Status | Last Updated |`

End command after displaying.

### Step 3: Show Mode (inline)

1. Find session file (try exact, `issue-`, `untracked-` prefixes)
2. If not found: list available sessions
3. Display: Status, Issue, Started, Hypotheses summary, Actions

End command after displaying.

### Step 4: Search Mode (inline)

Parse: `--search "query" [--status <status>] [--file <path>]`

1. Load `.tiki/debug/index.json`
2. Score matches: keyword in `keywords` (+2), `title` (+3), `rootCause` (+4), `errorPatterns` (+5)
3. Apply filters, sort by score
4. Display: `| # | Session | Status | Score | Root Cause |`

End command after displaying.

### Step 5: Check Similar Sessions

For new sessions (not resume/list/show/search):
- Read `.tiki/prompts/debug/start-session.md` for similarity matching
- If matches found (score >= 5): offer to view or continue

### Step 6: Session Initialization

If `--resume`: load existing session, display state, continue to hypothesis workflow.

If new session:
1. Create `.tiki/debug/` if needed
2. Generate filename: `issue-{N}-{kebab-title}.md` or `untracked-{kebab-symptom}.md`
3. Read `.tiki/prompts/debug/start-session.md` for document structure
4. Read `.tiki/prompts/debug/index-management.md` for index update

### Step 7: Gather Symptoms

Ask user:
1. What is failing?
2. Error messages/output?
3. When did it start?
4. Reproducible?

Auto-detect environment via Bash. Document in session file.

### Step 8: Hypothesis Workflow

Read `.tiki/prompts/debug/hypothesis-tracking.md` for:
- Forming 2-4 testable hypotheses
- Test strategy by hypothesis type
- Recording outcomes (REJECTED/CONFIRMED/INCONCLUSIVE)
- Progress summaries every 2-3 hypotheses
- Stuck detection after 4+ rejections

Loop: Form -> Test -> Record -> Iterate

### Step 9: Resolution

When root cause confirmed:
- Read `.tiki/prompts/debug/resolution-recording.md` for:
  - Root cause documentation
  - Solution recording
  - Lessons learned capture
  - Status update to resolved

### Step 10: Exit Options

At any breakpoint:
1. **Continue** - Keep testing
2. **Mark resolved** - Go to Step 9
3. **Pause** - Save progress, update status to "Paused"
4. **Abandon** - Record reason, mark abandoned

### Step 11: Update Index

After any session change:
- Read `.tiki/prompts/debug/index-management.md`
- Update `.tiki/debug/index.json` with session metadata

## State Files

| File | Purpose |
|------|---------|
| `.tiki/debug/index.json` | Session index (see schema notes below) |
| `.tiki/debug/{session}.md` | Session document |
| `.tiki/debug/archive/` | Archived sessions |

## Index Schema

`.tiki/debug/index.json` contains:
- `sessions[]`: id, filename, issue, title, type, status, createdAt, resolvedAt, rootCause, keywords, errorPatterns, affectedFiles, solution, archived

## Session Document Structure

```markdown
# Debug Session: {Title}
## Session Info (table: Started, Issue, Status, Last Updated)
## Symptoms
## Environment
## Hypotheses (H1, H2, ... with status tags)
## Investigation Log
## Root Cause
## Solution Applied
## Lessons Learned
```

## Integration

- From failed phase: suggest `/tiki:debug` after `/tiki:heal` fails
- Discoveries: add to `.tiki/queue/pending.json`
- Untracked to issue: offer to create GitHub issue from findings

## Notes

- Sessions persist across conversations
- Use `--resume` to continue
- Each hypothesis should be atomic and testable
- Index is auto-maintained; rebuild if corrupted
