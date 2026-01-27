---
type: prompt
name: tiki:add-issue
description: Create a new GitHub issue with intelligent prompting. Claude asks clarifying questions to flesh out the issue before creating it.
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
argument-hint: [title or description]
---

# Add Issue

Create a new GitHub issue with intelligent prompting. If the user provides a brief description, ask clarifying questions to create a well-structured issue.

## Usage

```
/tiki:add-issue
/tiki:add-issue "Add dark mode support"
/tiki:add-issue "Users can't login after password reset"
```

## Instructions

### Step 1: Parse Initial Input

Check what the user provided:

- **No input:** Start from scratch, ask what they want to create
- **Brief title:** Use as starting point, ask clarifying questions
- **Detailed description:** Extract info, confirm, and fill gaps

### Step 2: Detect Issue Type

Analyze the input to determine the likely type:

| Keywords | Type | Default Labels |
|----------|------|----------------|
| bug, fix, broken, error, crash, doesn't work, can't | `bug` | `bug` |
| add, new, feature, implement, support, enable | `feature` | `enhancement` |
| update, change, modify, improve, refactor | `enhancement` | `enhancement` |
| docs, documentation, readme, comment | `docs` | `documentation` |
| test, coverage, spec | `testing` | `testing` |
| security, vulnerability, auth, permission | `security` | `security` |

Tell the user what type you detected:

```
This looks like a **feature request**. I'll ask a few questions to create a complete issue.
```

### Step 3: Ask Clarifying Questions

Use AskUserQuestion to gather missing information. Adapt questions based on issue type:

#### For Features/Enhancements

```
1. **Problem:** What problem does this solve? Why do users need this?
2. **Acceptance Criteria:** How will we know this is complete? What should work?
3. **Context:** Any technical constraints, preferences, or related features?
4. **Priority:** How important is this? (critical / high / medium / low)
```

#### For Bugs

```
1. **Expected vs Actual:** What should happen vs what is happening?
2. **Reproduction Steps:** How can we reproduce this?
3. **Environment:** Where does this occur? (browser, OS, version, etc.)
4. **Severity:** How bad is this? (critical / high / medium / low)
```

#### For Documentation

```
1. **What's Missing:** What needs to be documented?
2. **Audience:** Who is this documentation for?
3. **Location:** Where should this documentation live?
```

**Important:**
- Don't ask questions if the user already provided the information
- Skip questions that aren't relevant to this specific issue
- Keep it conversational, not interrogation-like
- 2-4 questions max, combine related questions

### Step 4: Check for Related Issues

Search existing issues for potential duplicates or related work:

```bash
gh issue list --state all --search "<keywords from title>" --json number,title,state --limit 5
```

If related issues found:

```
I found some related issues:
- #23: "Add theme switching" (open)
- #15: "Dark mode for mobile" (closed)

Should I link to any of these, or is this separate work?
```

### Step 5: Check for Issue Template

Look for issue templates in the repository:

```bash
ls -la .github/ISSUE_TEMPLATE/ 2>/dev/null || ls -la .github/ 2>/dev/null | grep -i issue
```

If templates exist, use the appropriate one as a format guide.

### Step 6: Draft the Issue

Create a well-formatted issue draft:

```markdown
## Issue Draft

**Title:** Add dark mode support

**Type:** Feature
**Priority:** Medium
**Labels:** `enhancement`, `ui`

---

### Description

Users have requested the ability to switch between light and dark themes for better readability in low-light environments.

### Problem

Currently the app only has a light theme, which can cause eye strain when used at night or in dark rooms.

### Acceptance Criteria

- [ ] Toggle switch in Settings to enable/disable dark mode
- [ ] Dark theme applies to all screens
- [ ] User preference persists across sessions
- [ ] Respects system-level dark mode preference as default

### Technical Notes

Consider using CSS custom properties for theme colors to make switching efficient.

### Related Issues

- Related to #23 (theme switching infrastructure)

---

**Does this look good? Should I create it, or would you like to modify anything?**
```

### Step 7: Confirm and Create

Wait for user confirmation, then create:

```bash
gh issue create \
  --title "Add dark mode support" \
  --body "$(cat <<'EOF'
## Description

Users have requested the ability to switch between light and dark themes for better readability in low-light environments.

## Problem

Currently the app only has a light theme, which can cause eye strain when used at night or in dark rooms.

## Acceptance Criteria

- [ ] Toggle switch in Settings to enable/disable dark mode
- [ ] Dark theme applies to all screens
- [ ] User preference persists across sessions
- [ ] Respects system-level dark mode preference as default

## Technical Notes

Consider using CSS custom properties for theme colors to make switching efficient.

## Related Issues

- Related to #23 (theme switching infrastructure)

---
*Created via Tiki /tiki:add-issue*
EOF
)" \
  --label "enhancement" \
  --label "ui"
```

### Step 8: Confirm Creation

```
Created Issue #34: Add dark mode support

**Labels:** enhancement, ui
**URL:** https://github.com/owner/repo/issues/34

**Next steps:**
- Plan this issue: `/tiki:plan-issue 34`
- View the issue: `/tiki:get-issue 34`
- Create another: `/tiki:add-issue`
```

## Examples

### Example 1: Feature from Brief Title

```
User: /tiki:add-issue "Add dark mode"

Claude: This looks like a **feature request**. Let me ask a few questions to create a complete issue.

[Uses AskUserQuestion with:]
- What problem does dark mode solve for your users?
- What should the acceptance criteria be? (e.g., toggle location, persistence, system preference)

User: [Answers questions]

Claude: [Drafts issue, shows preview]

Does this look good? Should I create it?

User: Yes

Claude: Created Issue #34: Add dark mode support
```

### Example 2: Bug Report

```
User: /tiki:add-issue "Login broken after password reset"

Claude: This looks like a **bug report**. Let me gather some details.

[Uses AskUserQuestion with:]
- What happens when you try to login? Any error messages?
- Can you share the steps to reproduce this?

User: After resetting password, clicking login just refreshes the page. No error shown.
      Steps: 1) Reset password via email 2) Set new password 3) Try to login

Claude: [Drafts bug report with reproduction steps]

Does this capture the issue correctly?

User: Add that it works fine if you clear cookies

Claude: [Updates draft with workaround info, creates issue]

Created Issue #35: Login broken after password reset
Labels: bug
```

### Example 3: Starting from Scratch

```
User: /tiki:add-issue

Claude: What would you like to create an issue for? Give me a brief description or title.

User: We should probably add rate limiting to the API

Claude: This looks like a **feature/enhancement** for security. Let me ask a few questions.

[Uses AskUserQuestion with:]
- Which endpoints need rate limiting? All API routes or specific ones?
- What limits are you thinking? (e.g., 100 requests/minute per IP)
- How should we handle exceeded limits? (429 response, temporary block, etc.)

User: All auth endpoints, 10 requests per minute, return 429

Claude: [Drafts issue, creates]

Created Issue #36: Add rate limiting to authentication endpoints
Labels: enhancement, security
```

### Example 4: Detailed Input Needs Minimal Questions

```
User: /tiki:add-issue "Add export to PDF feature. Users need to export their reports as PDFs for sharing with clients. Should have options for page size (A4/Letter) and include company branding. High priority since clients are requesting this."

Claude: Great detail! This looks like a **feature request**. I have most of what I need.

One quick question: Should the PDF generation happen client-side or server-side? Any preference?

User: Server-side, we're using Node

Claude: [Drafts comprehensive issue from provided details + answer]

Created Issue #37: Add export to PDF feature
Labels: enhancement, high-priority
```

## Question Templates

Use these as starting points, but adapt based on context:

### Feature Questions
1. What problem does this solve?
2. What are the acceptance criteria?
3. Any technical constraints or preferences?
4. Priority level?

### Bug Questions
1. Expected vs actual behavior?
2. Steps to reproduce?
3. Environment details?
4. Severity/impact?

### Refactor Questions
1. What's the current pain point?
2. What's the desired end state?
3. Any breaking changes to consider?

## Error Handling

- **gh not installed:** "GitHub CLI (gh) is required. Install it and run `gh auth login`."
- **Not in repo:** "Not in a git repository. Navigate to your project directory."
- **No remote:** "No GitHub remote configured for this repository."
- **Permission denied:** "You don't have permission to create issues in this repository."

## Notes

- Adapt questions to what the user already provided - don't ask redundant questions
- Keep the conversation flowing naturally, not like a form
- Use AskUserQuestion for multi-choice questions (priority, type)
- Always show a draft before creating
- Link related issues when relevant
- The `gh` CLI must be installed and authenticated
