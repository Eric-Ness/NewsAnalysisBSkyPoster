---
type: prompt
name: tiki:review-queue
description: Review and process items discovered during execution. Use when there are queue items to review, create issues from, or dismiss.
allowed-tools: Read, Write, Bash, Glob
argument-hint: [--create-all] [--dismiss-all]
---

# Review Queue

Review items that accumulated during phase execution. These are potential issues, questions, and notes discovered by sub-agents during their work.

## Usage

```
/tiki:review-queue
/tiki:review-queue --create-all    # Create issues for all items
/tiki:review-queue --dismiss-all   # Clear all items
```

## Instructions

### Step 1: Read Queue

Load `.tiki/queue/pending.json`:

```json
{
  "items": [
    {
      "id": "q-001",
      "type": "potential-issue",
      "title": "Add rate limiting to login endpoint",
      "description": "During Phase 2, noticed no rate limiting on auth endpoints. Could be vulnerable to brute force attacks.",
      "source": {
        "issue": 34,
        "phase": 2
      },
      "priority": "medium",
      "labels": ["security", "enhancement"],
      "createdAt": "2026-01-10T11:00:00Z"
    },
    {
      "id": "q-002",
      "type": "question",
      "title": "Should password reset require email verification?",
      "description": "Implementing password reset flow - unclear if we need email verification or if a simple reset link is sufficient.",
      "source": {
        "issue": 34,
        "phase": 2
      },
      "createdAt": "2026-01-10T11:30:00Z"
    }
  ]
}
```

If queue is empty:
```
## Queue Empty

No items pending review.

Use `/tiki:state` to see current status.
```

### Step 2: Display Items

Show all queue items grouped by type:

```
## Queue Review

**5 items** pending review

### Potential Issues (3)

#### 1. Add rate limiting to login endpoint
- **Source:** Issue #34, Phase 2
- **Priority:** medium
- **Labels:** security, enhancement
- **Description:** No rate limiting on auth endpoints. Could be vulnerable to brute force attacks.

**Actions:** [Create Issue] [Dismiss] [Edit]

#### 2. Consider adding refresh tokens
- **Source:** Issue #34, Phase 2
- **Priority:** low
- **Labels:** enhancement
- **Description:** Current JWT implementation uses single tokens. Refresh tokens would improve security.

**Actions:** [Create Issue] [Dismiss] [Edit]

#### 3. Password strength validation needed
- **Source:** Issue #34, Phase 3
- **Priority:** medium
- **Labels:** security
- **Description:** No password strength requirements currently enforced.

**Actions:** [Create Issue] [Dismiss] [Edit]

---

### Questions (1)

#### 4. Should password reset require email verification?
- **Source:** Issue #34, Phase 2
- **Description:** Implementing password reset - unclear if email verification needed.

**Actions:** [Answer] [Convert to Issue] [Dismiss]

---

### Notes (1)

#### 5. Auth service architecture note
- **Source:** Issue #34, Phase 1
- **Description:** The auth service is tightly coupled to the user service. Consider extracting to separate module in future.

**Actions:** [Convert to Issue] [Add to CONCERNS.md] [Dismiss]

---

**Batch Actions:**
- Create all issues: `/tiki:review-queue --create-all`
- Dismiss all: `/tiki:review-queue --dismiss-all`

Or process individually below.
```

### Step 3: Process Items

Handle each item based on user input:

#### Create Issue

When user wants to create a GitHub issue:

```bash
gh issue create --title "Add rate limiting to login endpoint" --body "## Background
Discovered during implementation of Issue #34 (Add user authentication), Phase 2.

## Description
No rate limiting on auth endpoints. Could be vulnerable to brute force attacks.

## Suggested Priority
Medium

---
*Created from Tiki queue*" --label "security" --label "enhancement"
```

After creation:
```
Created Issue #37: Add rate limiting to login endpoint
Labels: security, enhancement

[Item removed from queue]
```

#### Dismiss Item

Remove from queue without action:

```
Dismissed: Add rate limiting to login endpoint

[Item removed from queue]
```

#### Answer Question

For question type items:

```
User: "Yes, password reset should require email verification"

Noted. Adding to project context.

Options:
1. Create issue to implement email verification
2. Add note to CLAUDE.md
3. Just dismiss (answer recorded in conversation)
```

#### Convert Note to Issue

For notes that should become tracked work:

```bash
gh issue create --title "Decouple auth service from user service" --body "..."
```

#### Add to CONCERNS.md

For architectural notes:

```
Added to CONCERNS.md:
- Auth service is tightly coupled to user service (consider extracting)

[Item removed from queue]
```

### Step 4: Update Queue

After processing each item, update `.tiki/queue/pending.json`:

Remove processed items:
```json
{
  "items": [
    // remaining items only
  ],
  "processed": [
    {
      "id": "q-001",
      "action": "created-issue",
      "issueNumber": 37,
      "processedAt": "2026-01-10T15:00:00Z"
    },
    {
      "id": "q-002",
      "action": "dismissed",
      "processedAt": "2026-01-10T15:01:00Z"
    }
  ]
}
```

### Step 5: Summary

After processing:

```
## Queue Processing Complete

**Processed 5 items:**
- 2 issues created (#37, #38)
- 1 question answered
- 1 note added to CONCERNS.md
- 1 item dismissed

**Queue now empty.**
```

## Queue Item Types

| Type | Description | Common Actions |
|------|-------------|----------------|
| `potential-issue` | Work that should be tracked | Create issue, Dismiss |
| `question` | Needs user input | Answer, Convert to issue |
| `note` | Observation or concern | Add to docs, Convert to issue |
| `blocker` | Something blocking progress | Investigate, Create issue |
| `tech-debt` | Code quality concern | Create issue, Add to CONCERNS.md |

## Queue Item Format

```json
{
  "id": "q-001",
  "type": "potential-issue",
  "title": "Short title",
  "description": "Detailed description of the item",
  "source": {
    "issue": 34,
    "phase": 2
  },
  "priority": "high|medium|low",
  "labels": ["label1", "label2"],
  "createdAt": "2026-01-10T11:00:00Z"
}
```

## Batch Operations

### --create-all

Create GitHub issues for all `potential-issue` and `tech-debt` items:

```
Creating issues for 3 items...

Created #37: Add rate limiting to login endpoint
Created #38: Consider adding refresh tokens
Created #39: Password strength validation needed

3 issues created. Queue cleared.
```

### --dismiss-all

Clear all items without action:

```
Dismissed 5 items.
Queue cleared.
```

## Integration with Execute

The `/tiki:execute` skill adds items to the queue when sub-agents report discoveries:

```
Sub-agent output:
"DISCOVERED: Consider adding rate limiting to prevent brute force attacks"

→ Added to queue:
{
  "type": "potential-issue",
  "title": "Consider adding rate limiting",
  "description": "Prevent brute force attacks on auth endpoints",
  "source": { "issue": 34, "phase": 2 }
}
```

## Notes

- Queue items are suggestions, not requirements
- Users have full control over what becomes an issue
- Dismissed items are logged in `processed` for reference
- Queue should be reviewed after each execution completes
- The `/tiki:execute` skill suggests reviewing queue when items exist
