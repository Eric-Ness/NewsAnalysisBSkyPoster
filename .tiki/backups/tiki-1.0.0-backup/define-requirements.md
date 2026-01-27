---
type: prompt
name: tiki:define-requirements
description: Interactively define/update project requirements. Analyzes codebase and issues to propose requirements.
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
argument-hint: [--from-issues] [--refresh] [--category <name>]
---

# Define Requirements

Interactively define or update project requirements. Creates `.tiki/REQUIREMENTS.md` (human-readable) and `.tiki/requirements.json` (machine-readable).

## Usage

```text
/tiki:define-requirements
/tiki:define-requirements --from-issues    # Seed from GitHub issues
/tiki:define-requirements --refresh        # Sync with codebase state
/tiki:define-requirements --category "Security"
```

## Instructions

### Step 0: Parse Arguments

Parse flags from `$ARGUMENTS`:

- `--from-issues`: Seed requirements from open GitHub issues (skip codebase analysis)
- `--refresh`: Force re-analysis and sync with current state
- `--category <name>`: Focus on a specific category only

### Step 1: Check Existing Requirements

Check for `.tiki/REQUIREMENTS.md` and `.tiki/requirements.json`.

**If files exist AND --refresh NOT set:**

Use AskUserQuestion:

```text
Existing requirements found. What would you like to do?
1. Update existing - Add new requirements while keeping existing ones
2. View existing - Display current requirements
3. Overwrite - Start fresh (existing will be backed up)
4. Cancel - Exit without changes
```

Handle choices:

- Update: Load existing, continue to Step 2
- View: Display .tiki/REQUIREMENTS.md and exit
- Overwrite: Backup files, continue to Step 2
- Cancel: Exit with "No changes made."

**If --refresh set:**

Backup existing files and proceed to refresh workflow.

### Step 2: Load Context Files

Load available project context:

```text
Check and read if exists:
- PROJECT.md -> projectContext (vision, goals, constraints)
- CLAUDE.md -> claudeContext (conventions, patterns)
- .tiki/STACK.md -> stackContext (languages, frameworks)
```

Display summary:

```text
## Context Loaded
| Source | Status | Key Information |
|--------|--------|-----------------|
| PROJECT.md | Found/Not Found | [summary] |
| CLAUDE.md | Found/Not Found | [summary] |
| .tiki/STACK.md | Found/Not Found | [summary] |
```

### Step 3: Mode Detection and Routing

Determine execution mode and load appropriate conditional prompts.

#### Refresh Mode (--refresh flag)

If `--refresh` is set, execute inline refresh workflow:

1. Load existing `.tiki/requirements.json`
2. Re-run codebase analysis
3. For each requirement:
   - Check if code exists (pending -> implemented)
   - Verify code still exists (implemented -> flag if removed)
4. Sync with GitHub issues via `gh issue view {number} --json state`
5. Generate diff summary showing status changes
6. Write updated files

Display refresh results:

```text
## Refresh Complete
### Status Changes
| Requirement | Previous | Current | Reason |
### Issues Synced
| Issue | Status | Linked Requirements |
```

#### From-Issues Mode (--from-issues flag)

If `--from-issues` is set:

- Read `.tiki/prompts/define-requirements/from-issues-mode.md`
- Follow instructions for issue-to-requirement mapping
- Skip codebase analysis (Step 4)
- Proceed to Step 5

#### Standard Mode (default)

For full analysis and interactive definition:

- Read `.tiki/prompts/define-requirements/ai-suggestions.md`
- Analyze codebase for existing functionality
- Generate proposed requirements from analysis
- Proceed to Step 5

### Step 4: Codebase Analysis (Standard Mode Only)

When in standard mode, analyze codebase for existing functionality. Details in `.tiki/prompts/define-requirements/ai-suggestions.md`.

Key patterns to detect:

- Commands (CLI tools, Claude Code commands)
- API endpoints (REST routes)
- Authentication/authorization
- Test coverage gaps

Build functionality map and cross-reference with GitHub issues.

### Step 5: Generate Proposed Requirements

Transform analysis into structured requirements.

**Category codes:**

| Code | Category |
|------|----------|
| CORE | Core Functionality |
| SEC | Security |
| QUAL | Quality |
| PERF | Performance |
| DOC | Documentation |

**Requirement format:** See `.tiki/schemas/requirements.schema.json`

Display proposed requirements grouped by category with status indicators.

### Step 6: Interactive Refinement (Conditional)

When user wants to add/edit/delete requirements or reorganize categories:

- Read `.tiki/prompts/define-requirements/interactive-mode.md`
- Follow interactive refinement loop until user accepts

When managing categories (create/rename/merge):

- Read `.tiki/prompts/define-requirements/category-management.md`
- Follow category CRUD operations

Present refinement menu:

```text
## Requirement Refinement
N requirements proposed. What would you like to do?
1. Accept - Save as-is
2. Edit - Modify a requirement
3. Add - Create new requirement
4. Remove - Delete a requirement
5. Reorganize - Move/rename categories
6. Review flagged - Examine flagged items
```

Loop until user selects "Accept".

### Step 7: Generate Output Files

After user accepts, write both files.

**Write .tiki/REQUIREMENTS.md:**

```markdown
# Requirements

## Coverage Summary
[summary of what's covered]

## v1 Requirements

### Core Functionality
- **CORE-01**: [requirement text]
  - *Verify: [type]* - [description]
  - *Implemented by: #[issue]* or *Status: Pending*
```

**Write .tiki/requirements.json:**

Structure per `.tiki/schemas/requirements.schema.json`:

- `version`: Schema version ("1.0")
- `createdAt`, `updatedAt`: ISO timestamps
- `categories[]`: Category objects with requirements
- `versions`: Maps version names to requirement IDs
- `outOfScope`: Excluded items

The JSON file is authoritative; .tiki/REQUIREMENTS.md is the human-readable view.

### Step 8: Display Completion Summary

```text
## Requirements Definition Complete

### Files Created
| File | Path |
|------|------|
| Human-readable | .tiki/REQUIREMENTS.md |
| Machine-readable | .tiki/requirements.json |

### Summary
Total Requirements: N
- Implemented: X (Y%)
- Pending: X (Y%)

### By Category
| Category | Code | Requirements | Implemented |
|----------|------|--------------|-------------|

### Next Steps
1. Review .tiki/REQUIREMENTS.md for accuracy
2. Use /tiki:plan-issue to plan work against requirements
3. Run /tiki:define-requirements --refresh to update later
```

## State Files

- `.tiki/REQUIREMENTS.md` - Human-readable requirements document
- `.tiki/requirements.json` - Machine-readable requirements (authoritative)
- `.tiki/requirements.draft.json` - Partial state if session interrupted

## Error Handling

### GitHub CLI Not Available

```text
Error: GitHub CLI (gh) not installed or not authenticated.
Options:
1. Continue without GitHub integration
2. Cancel and fix authentication first
```

### Corrupted requirements.json

```text
Error: Existing requirements.json is corrupted.
Options:
1. Start fresh (backup corrupted file)
2. Attempt recovery
3. Restore from backup
4. Cancel
```

### No Issues Found (--from-issues)

```text
Error: No open GitHub issues found.
Options:
1. Create issues first
2. Run without --from-issues
3. Cancel
```

## Options

| Option | Description |
|--------|-------------|
| `--from-issues` | Seed requirements from open GitHub issues |
| `--refresh` | Re-analyze codebase and sync requirement status |
| `--category <name>` | Focus on specific category |

## Notes

- **.tiki/REQUIREMENTS.md** is human-readable, editable, reviewable in GitHub
- **requirements.json** is for tooling integration and automated workflows
- Run `--refresh` regularly to keep requirements in sync with codebase
- Use `--from-issues` to bootstrap requirements from existing issues
- For interactive operations: see `.tiki/prompts/define-requirements/interactive-mode.md`
- For issue seeding: see `.tiki/prompts/define-requirements/from-issues-mode.md`
- For codebase analysis: see `.tiki/prompts/define-requirements/ai-suggestions.md`
- For category management: see `.tiki/prompts/define-requirements/category-management.md`
