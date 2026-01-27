---
type: prompt
name: tiki:get-issue
description: Fetch and display GitHub issues with context. Use when the user wants to see a GitHub issue, review issues, or start working on an issue by number.
allowed-tools: Bash, Read, Write, AskUserQuestion, Skill
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

5. **Offer Next Steps (if enabled)**

   Check if menus are enabled:
   1. Read `.tiki/config.json`
   2. If `workflow.showNextStepMenu` is `false`, skip this step and suggest: "Ready to plan? Use `/tiki:plan-issue <number>`"
   3. If not set or `true`, proceed with interactive menu

   **Only show menu on SUCCESS** (issue found and displayed). Do NOT show menu if issue was not found.

   Use `AskUserQuestion` to present workflow options:

   **Options:**
   - "Review issue" (description: "Identify concerns before planning") → then invoke Skill tool with `tiki:review-issue {issue_number}`
   - "Plan issue" (description: "Break into executable phases") → then invoke Skill tool with `tiki:plan-issue {issue_number}`
   - "Research" (description: "Explore unfamiliar domain first") → then invoke Skill tool with `tiki:research {issue_number}`
   - "Done for now" (description: "Exit without further action") → end session

   Based on user selection:
   - If user selects "Review issue" → invoke `Skill` tool with skill="tiki:review-issue" args="{issue_number}"
   - If user selects "Plan issue" → invoke `Skill` tool with skill="tiki:plan-issue" args="{issue_number}"
   - If user selects "Research" → invoke `Skill` tool with skill="tiki:research" args="{issue_number}"
   - If user selects "Done for now" → end without further action

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

[AskUserQuestion with options: Review issue, Plan issue, Research, Done for now]
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
- After displaying issue(s), offers interactive next-step menu (if enabled in config)
- Menu can be disabled by setting `workflow.showNextStepMenu: false` in `.tiki/config.json`
