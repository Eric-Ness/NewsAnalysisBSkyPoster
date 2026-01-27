---
type: prompt
name: tiki:add-issue
description: Create a new GitHub issue with intelligent prompting. Claude asks clarifying questions to flesh out the issue before creating it.
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
argument-hint: [title or description]
---

# Add Issue

Create a new GitHub issue with intelligent prompting. Ask clarifying questions to create well-structured issues.

## Usage

```
/tiki:add-issue
/tiki:add-issue "Add dark mode support"
/tiki:add-issue "Users can't login after password reset"
```

## Instructions

### Step 1: Parse Initial Input

Check what the user provided:

- **No input:** Ask what they want to create
- **Brief title:** Use as starting point, ask clarifying questions
- **Detailed description:** Extract info, confirm, fill gaps

### Step 2: Detect Issue Type

Read `.tiki/prompts/add-issue/label-suggestions.md` for issue type detection and label selection.

Tell the user what type you detected (bug, feature, enhancement, docs, testing, security).

### Step 3: Ask Clarifying Questions

Read `.tiki/prompts/add-issue/question-templates.md` for question templates by issue type.

Use AskUserQuestion to gather missing information. Guidelines:

- Skip questions if user already provided the information
- Keep it conversational, 2-4 questions max
- Combine related questions

### Step 4: Check for Related Issues

Search existing issues for duplicates or related work:

```bash
gh issue list --state all --search "<keywords>" --json number,title,state --limit 5
```

If found, ask if the issue should link to them.

### Step 5: Check for Issue Template

```bash
ls -la .github/ISSUE_TEMPLATE/ 2>/dev/null || ls -la .github/ 2>/dev/null | grep -i issue
```

If templates exist, use as format guide.

### Step 6: Draft the Issue

Create a well-formatted issue draft with:

- **Title** - Clear, actionable
- **Type/Priority/Labels** - Based on detection
- **Description** - What and why
- **Acceptance Criteria** - Checkboxes for completion
- **Technical Notes** - If relevant
- **Related Issues** - If found

Show draft and ask: "Does this look good? Should I create it, or would you like to modify anything?"

### Step 7: Confirm and Create

Wait for user confirmation, then:

```bash
gh issue create \
  --title "<title>" \
  --body "$(cat <<'EOF'
## Description
<description>

## Acceptance Criteria
- [ ] <criteria>

---
*Created via Tiki /tiki:add-issue*
EOF
)" \
  --label "<label1>" \
  --label "<label2>"
```

### Step 8: Confirm Creation

Report:

- Issue number and title
- Labels applied
- URL
- Next steps: `/tiki:plan-issue N`, `/tiki:get-issue N`

## Error Handling

- **gh not installed:** "GitHub CLI (gh) is required. Install it and run `gh auth login`."
- **Not in repo:** "Not in a git repository. Navigate to your project directory."
- **No remote:** "No GitHub remote configured for this repository."
- **Permission denied:** "You don't have permission to create issues in this repository."

## Notes

- Adapt questions to what the user already provided
- Keep conversation flowing naturally
- Always show draft before creating
- Link related issues when relevant
