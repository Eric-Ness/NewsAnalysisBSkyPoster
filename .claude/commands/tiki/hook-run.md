---
type: prompt
name: tiki:hook-run
description: Manually trigger a lifecycle hook script. Use for testing hooks or running them outside normal workflow.
allowed-tools: Read, Bash, Glob
argument-hint: <hook-name> [--env KEY=VALUE]...
---

# Hook Run

Manually execute a lifecycle hook script.

## Usage

```
/tiki:hook-run pre-ship
/tiki:hook-run post-commit --env TIKI_COMMIT_SHA=abc123
/tiki:hook-run phase-complete --env TIKI_PHASE_NUMBER=2 --env TIKI_PHASE_STATUS=completed
```

## Instructions

### Step 1: Parse Arguments

Extract hook name from first argument. Parse `--env` flags for custom environment variables.

If no hook name provided, show usage and list available hooks:
- pre-ship, post-ship
- pre-execute, post-execute
- pre-commit, post-commit
- phase-start, phase-complete

### Step 2: Load Configuration

Read `.tiki/config.json` for:
- `extensions.lifecycleScripts.directory` (default: `.tiki/hooks`)
- `extensions.lifecycleScripts.timeout` (default: 30000)
- `extensions.lifecycleScripts.enabled` (if false, warn but still allow manual run)

### Step 3: Locate Hook File

Check for hook file in configured directory:
- `<directory>/<hook-name>` (Unix-style)
- `<directory>/<hook-name>.sh` (explicit shell)
- `<directory>/<hook-name>.ps1` (PowerShell on Windows)

If not found, show error with expected path and exit.

### Step 4: Auto-Populate Context

Read `.tiki/prompts/hooks/manual-trigger.md` for context auto-population and suggested environment variables.

If Tiki state exists (`.tiki/state/current.json`):
- Auto-populate `TIKI_ISSUE_NUMBER` from state
- Auto-populate `TIKI_ISSUE_TITLE` from state
- Auto-populate `TIKI_PHASE_NUMBER` from state (if in execution)
- User-provided `--env` values override auto-populated values

If no state:
- Use only user-provided `--env` values
- Suggest common env vars for the specific hook being run

### Step 5: Execute Hook

Read `.tiki/prompts/hooks/execute-hook.md` for execution workflow.
On Windows, also read `.tiki/prompts/hooks/windows-support.md`.

Run the hook with:
- Configured timeout
- Combined environment variables
- Capture stdout and stderr

### Step 6: Report Result

Display comprehensive output:

```
## Hook Execution: <hook-name>

Path: <full-path-to-hook>
Environment:
  TIKI_ISSUE_NUMBER=<value>
  ...

Exit code: <code>
Duration: <ms>ms

### Output
<stdout>

### Errors (if any)
<stderr>

Result: SUCCESS | FAILED
```

## Notes

- Useful for testing hooks before actual workflow
- Manual runs don't affect Tiki state
- Use --env to simulate different scenarios
- Hook name is case-sensitive
