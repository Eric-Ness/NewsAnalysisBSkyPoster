---
type: prompt
name: tiki:get-issue
description: Fetch and display GitHub issues with context. Use when the user wants to see a GitHub issue, review issues, or start working on an issue by number.
allowed-tools: Bash, Read, Write
argument-hint: <issue-number> [additional-numbers...]
---

# Get Issue

Retrieve one or more GitHub issues and display them with useful context.

## Usage

```
/tiki:get-issue 34
/tiki:get-issue 34 45 67
```

## Instructions

1. **Parse the issue number(s)** from the user's request
   - Single issue: `/tiki:get-issue 34`
   - Multiple issues: `/tiki:get-issue 34 45 67`
   - If no number provided, ask the user which issue they want

2. **Fetch issue(s) using GitHub CLI**
   ```bash
   gh issue view <number> --json number,title,body,state,labels,assignees,milestone,createdAt,updatedAt,comments
   ```

3. **Display each issue** in a readable format:
   ```
   ## Issue #<number>: <title>

   **State:** <open/closed>
   **Labels:** <labels or "None">
   **Assignees:** <assignees or "Unassigned">
   **Milestone:** <milestone or "None">
   **Created:** <date>
   **Updated:** <date>

   ### Description
   <body content>

   ### Comments (<count>)
   <recent comments if any>
   ```

4. **Provide context** after displaying:
   - If issue has labels like `bug`, `feature`, `enhancement`, mention what type of work this is
   - If issue references other issues, note the dependencies
   - Suggest next steps (e.g., "Ready to plan this issue? Use `/tiki:plan-issue <number>`")

## Examples

### Single Issue
```
User: /tiki:get-issue 34

Claude:
## Issue #34: Add user authentication

**State:** open
**Labels:** feature, high-priority
**Assignees:** @username
**Milestone:** v2.0
**Created:** 2026-01-05
**Updated:** 2026-01-09

### Description
We need to add user authentication to the API. Requirements:
- JWT-based auth
- Login/logout endpoints
- Password hashing with bcrypt
- Session management

### Comments (2)
**@reviewer** (2026-01-07): Should we also add refresh tokens?
**@username** (2026-01-08): Yes, good idea. Added to requirements.

---
This is a **feature** request marked as **high-priority**.
Ready to plan? Use `/tiki:plan-issue 34`
```

### Multiple Issues
```
User: /tiki:get-issue 34 35 36

Claude: [Displays all three issues in sequence, then summarizes]

## Summary
- #34: Add user authentication (feature, high-priority)
- #35: Fix login redirect bug (bug, medium-priority)
- #36: Update documentation (docs, low-priority)

Which issue would you like to work on?
```

## Error Handling

- **Issue not found:** "Issue #<number> not found. Check the issue number and try again."
- **No gh CLI:** "GitHub CLI (gh) is not installed or not authenticated. Run `gh auth login` first."
- **No repo context:** "Not in a git repository or no remote configured."

## Notes

- This skill uses the `gh` CLI which must be installed and authenticated
- Works with the current repository context
- For planning an issue after viewing, suggest `/tiki:plan-issue <number>`
