---
type: prompt
name: tiki:pause
description: Save current execution state mid-phase for later resumption. Use when you need to stop work and continue later.
allowed-tools: Read, Write, Glob
argument-hint: ["reason for pausing"]
---

# Pause

Save the current execution state so work can be resumed later. Captures context, progress, and decisions made.

## Usage

```
/tiki:pause
/tiki:pause "reason for pausing"
```

## Instructions

### Step 1: Check for Active Work

Read `.tiki/state/current.json` to verify there's active work to pause.

If no active work:
```
Nothing to pause. No active execution in progress.
Use `/tiki:state` to see current status.
```

### Step 2: Gather Current Context

Collect information about the current state:

1. **Active issue and phase** from `current.json`
2. **Phase details** from `.tiki/plans/issue-N.json`
3. **Recent file changes** (git status)
4. **Current progress within the phase**

### Step 3: Create Context Snapshot

Save detailed context to `.tiki/context/issue-N-phase-M.json`:

```json
{
  "issue": {
    "number": 34,
    "title": "Add user authentication"
  },
  "phase": {
    "number": 2,
    "title": "Add login endpoint",
    "content": "<full phase content>"
  },
  "pausedAt": "2026-01-10T14:30:00Z",
  "reason": "User requested pause",
  "progress": {
    "description": "Implemented POST /api/login, still need to add tests",
    "filesModified": [
      "src/routes/auth.ts",
      "src/services/auth.ts"
    ],
    "filesCreated": [],
    "tasksCompleted": [
      "Created login route",
      "Implemented password validation",
      "Added JWT generation"
    ],
    "tasksRemaining": [
      "Add unit tests",
      "Add integration tests"
    ]
  },
  "decisions": [
    "Used bcrypt for password hashing (industry standard)",
    "JWT expires in 24 hours (can be configured later)"
  ],
  "notes": "The auth service is working but needs error handling for edge cases",
  "previousPhaseSummaries": [
    {
      "number": 1,
      "title": "Setup auth middleware",
      "summary": "Created JWT validation middleware"
    }
  ]
}
```

### Step 4: Update State Files

Update `.tiki/state/current.json`:

```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "paused",
  "startedAt": "2026-01-10T10:00:00Z",
  "lastActivity": "2026-01-10T14:30:00Z",
  "pausedAt": "2026-01-10T14:30:00Z",
  "pauseReason": "User requested pause",
  "completedPhases": [...]
}
```

Update the phase in `.tiki/plans/issue-N.json`:

```json
{
  "number": 2,
  "status": "paused",
  ...
}
```

### Step 5: Confirm Pause

Display confirmation:

```
## Execution Paused

**Issue #34:** Add user authentication
**Phase 2:** Add login endpoint

### Progress Saved
- Files modified: src/routes/auth.ts, src/services/auth.ts
- Completed: Login route, password validation, JWT generation
- Remaining: Unit tests, integration tests

### Context Saved
`.tiki/context/issue-34-phase-2.json`

### To Resume
```
/tiki:resume 34
```

Or continue from current phase:
```
/tiki:execute 34 --from 2
```
```

## Context Gathering

When pausing, try to capture:

| Information | Source | Purpose |
|-------------|--------|---------|
| Files modified | `git status` | Know what was touched |
| Tasks completed | Conversation context | Track progress |
| Tasks remaining | Phase verification list | Know what's left |
| Decisions made | Conversation context | Preserve rationale |
| Blockers/notes | User input | Context for resume |

## Pause Reasons

Common reasons for pausing:

- **User requested** - Manual pause via `/pause`
- **Context limit** - Approaching context window limit
- **Blocked** - Waiting for external input or dependency
- **End of session** - User ending work session
- **Error encountered** - Need to investigate before continuing

## Automatic Pause Triggers

The `/execute` skill may auto-pause when:

1. Context window is getting full (~90% used)
2. A phase encounters an error that needs investigation
3. User input is required to continue

When auto-paused, the system saves context and notifies:

```
## Auto-Paused

Execution paused: Context limit approaching

Progress has been saved. Resume with:
```
/tiki:resume 34
```
```

## State File Updates

### Before Pause

`.tiki/state/current.json`:
```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "in_progress",
  ...
}
```

### After Pause

`.tiki/state/current.json`:
```json
{
  "activeIssue": 34,
  "currentPhase": 2,
  "status": "paused",
  "pausedAt": "2026-01-10T14:30:00Z",
  "pauseReason": "User requested pause",
  ...
}
```

## Notes

- Always save context before pausing - this is critical for resume
- Include enough detail that a fresh Claude session can continue
- Capture decisions and rationale, not just what files changed
- The context file is the primary source for `/resume`
