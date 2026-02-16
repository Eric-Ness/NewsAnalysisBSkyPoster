---
type: prompt
name: tiki:release-yolo
description: Automated release execution (plan, execute, ship all issues)
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion, Skill, Task
argument-hint: <version> [--skip-verify] [--no-tag] [--dry-run] [--continue] [--from <issue>]
---

# Release YOLO

Automated release execution that plans, executes, and ships all issues in a release.

## Usage

```text
/tiki:release-yolo v1.1                   # Full automated workflow
/tiki:release-yolo v1.1 --skip-verify     # Skip requirement verification
/tiki:release-yolo v1.1 --no-tag          # Don't create git tag
/tiki:release-yolo v1.1 --dry-run         # Show what would happen
/tiki:release-yolo v1.1 --continue        # Resume paused execution
/tiki:release-yolo v1.1 --from 42         # Start from specific issue
```

## Flow

### Step 1: Parse Arguments

Extract from `$ARGUMENTS`: version, --skip-verify, --no-tag, --dry-run, --continue, --from N.

If no version (and not --continue): show usage and exit.

### Step 2: Handle --continue

If `--continue` flag present:

1. Read main state at `.tiki/state/current.json`
2. Look for execution with `type: "release"` in `activeExecutions` array
3. If found, read `.tiki/prompts/release-yolo/resume.md` and follow resume workflow
4. Continue from saved position in the release execution object

### Step 3: Load Release

```bash
VERSION="${version}"
[[ ! "$VERSION" =~ ^v ]] && VERSION="v${VERSION}"
cat ".tiki/releases/${VERSION}.json" 2>/dev/null || echo "NOT_FOUND"
```

If not found or empty: show error with available releases.

### Step 4: Calculate Dependency Order

Analyze issue dependencies (look for "depends on #N" in issue bodies). Order issues so dependencies are processed first. If circular, warn and use original order.

### Step 5: Pre-Flight Display

```text
## Release YOLO: {version}

### Execution Order

| # | Issue | Title | Dependencies | Status |
|---|-------|-------|--------------|--------|
| 1 | #34 | Title | none | not_planned |

### Configuration

| Setting | Value |
|---------|-------|
| TDD Mode | {from .tiki/config.json} |
| Skip Verification | {yes/no} |
| Create Tag | {yes/no} |
```

If `--dry-run`: show plan and exit.

Otherwise, confirm with user before proceeding.

### Step 6: Initialize State

Add release execution to `.tiki/state/current.json` activeExecutions array:

```javascript
// Generate execution ID with release-specific format
const executionId = `exec-release-${VERSION.replace(/\./g, '-')}-${uuid.substring(0, 8)}`;

// Add to activeExecutions in main state
const releaseExecution = {
  "id": executionId,
  "type": "release",
  "status": "executing",
  "release": VERSION,
  "currentIssue": null,
  "issueOrder": [34, 36, 20],  // From dependency order calculation
  "completedIssues": [],
  "failedIssues": [],
  "flags": { "skipVerify": false, "noTag": false },
  "startedAt": new Date().toISOString(),
  "lastActivity": new Date().toISOString()
};

// Read current state, add execution, write back
state.activeExecutions.push(releaseExecution);
```

If main state doesn't exist, create with schema v2 structure first.

### Step 7: Issue Processing Loop

For each issue in dependency order (starting from --from position if provided):

#### 7a: Display Issue Header

```text
---
## Issue {index}/{total}: #{number} - {title}
```

#### 7b: Update Release Execution State

Update the release execution in `activeExecutions`:

```javascript
// Find and update release execution
const releaseExec = state.activeExecutions.find(e => e.type === "release");
releaseExec.currentIssue = issueNumber;
releaseExec.lastActivity = new Date().toISOString();
// Write state
```

#### 7c: Plan Stage

If no plan exists:

1. Read `.tiki/prompts/release-yolo/plan-stage.md`
2. Follow planning workflow

#### 7d: Execute Stage

1. Read `.tiki/prompts/release-yolo/execute-stage.md`
2. Invoke `/tiki:execute {number}` using the Skill tool
3. **Validation Checkpoint**: After execute returns, verify state was updated:
   - Read `.tiki/state/current.json`
   - Check that `activeExecutions` contains an execution for this issue OR `executionHistory` contains a completed execution for this issue
   - Check that the issue execution has `currentPhase > 0` OR `completedPhases` is non-empty
   - If validation fails: display warning and offer recovery options (Retry execute, Manual state update, Continue anyway)
4. If failure, read `.tiki/prompts/release-yolo/error-recovery.md`

#### 7e: Ship Stage

1. Read `.tiki/prompts/release-yolo/ship-stage.md`
2. Invoke `/tiki:ship {number}`
3. Update release execution state:
   ```javascript
   releaseExec.completedIssues.push(issueNumber);
   releaseExec.currentIssue = null;
   releaseExec.lastActivity = new Date().toISOString();
   ```
4. The individual issue's execution (if any) moves to `executionHistory`

### Step 8: Requirement Verification

If requirements exist AND not --skip-verify:

1. Read `.tiki/prompts/release-yolo/verification.md`
2. Follow verification workflow

### Step 9: Ship Release

Handle any failed issues (ship anyway, remove, or abort).

Create git tag (unless --no-tag):

```bash
git tag -a "${VERSION}" -m "Release ${VERSION}"
git push origin "${VERSION}"
```

Close milestone if linked. Archive release file.

Move release execution to history:

```javascript
// Find the release execution
const releaseExec = state.activeExecutions.find(e => e.type === "release");

// Update final status
releaseExec.status = "completed";
releaseExec.completedAt = new Date().toISOString();

// Move from activeExecutions to executionHistory
state.activeExecutions = state.activeExecutions.filter(e => e.type !== "release");
state.executionHistory.push(releaseExec);

// Write updated state
```

Update version.json with changelog entry for completed issues.

### Step 10: Completion Summary

```text
## Release {version} Shipped!

| Metric | Value |
|--------|-------|
| Issues Completed | {n}/{total} |
| Phases Executed | {count} |
| Requirements Verified | {n}/{total} |

### Issues Completed

| Issue | Title | Phases |
|-------|-------|--------|
| #{n} | {title} | {count} |
```

## Error Handling

- Release not found: Show available releases
- GitHub CLI unavailable: Show auth instructions
- Circular dependencies: Warn and use original order
- State corrupted: Read error-recovery.md for options
- Concurrent execution: Offer continue/restart/cancel

## Edge Cases

- Empty release: Error, suggest adding issues
- All issues complete: Skip to verification/shipping
- Single issue: Handle normally, skip dependency analysis
- Resume after issue removal: Offer continue or cancel
