---
type: prompt
name: tiki:create-issues
description: Batch create GitHub issues from queue items or code assessment findings. Use when you want to create multiple issues from discovered items or assessment reports.
allowed-tools: Read, Bash, Glob, Grep
argument-hint: [--from-queue] [--from-assessment] [--labels] [--priority <level>] [--dry-run]
---

# Create Issues

Batch-creates GitHub issues from the Tiki queue or from a code quality assessment report.

## Usage

```
/tiki:create-issues                        # Interactive mode - shows sources and prompts
/tiki:create-issues --from-queue           # Create issues from pending queue items
/tiki:create-issues --from-assessment      # Create issues from CODE_QUALITY_ASSESSMENT.md
/tiki:create-issues --dry-run              # Preview issues without creating
/tiki:create-issues --labels               # Auto-apply labels based on category
/tiki:create-issues --priority high        # Set priority labels
```

## Instructions

### Step 1: Determine Source

Check which source to use:

#### If `--from-queue` specified or no arguments:

Read `.tiki/queue/pending.json`:

```json
{
  "items": [
    {
      "id": "q-001",
      "type": "potential-issue",
      "title": "Add rate limiting to login endpoint",
      "description": "No rate limiting on auth endpoints. Could be vulnerable to brute force attacks.",
      "source": {
        "issue": 34,
        "phase": 2
      },
      "priority": "medium",
      "labels": ["security", "enhancement"],
      "createdAt": "2026-01-10T11:00:00Z"
    }
  ]
}
```

#### If `--from-assessment` specified:

Read `docs/CODE_QUALITY_ASSESSMENT.md` and parse findings sections:

```markdown
## Findings

### Security (Score: 65/100)

#### Critical
- **Missing CSRF Protection** - POST actions lack ValidateAntiForgeryToken
  - Files: `Controllers/UserController.cs`, `Controllers/OrderController.cs`
  - Recommendation: Add [ValidateAntiForgeryToken] to all POST actions

#### High Priority
- **Hardcoded Connection String** - Database credentials in appsettings.json
  - Files: `appsettings.json`
  - Recommendation: Use environment variables or Azure Key Vault
```

### Step 2: Display Preview

Show what will be created:

```
## Create Issues Preview

**Source:** Queue (3 items) / Assessment (7 findings)

### Issues to Create

#### 1. Add rate limiting to login endpoint
- **Priority:** medium
- **Labels:** security, enhancement
- **Source:** Queue item from Issue #34, Phase 2

#### 2. Missing CSRF Protection
- **Priority:** critical
- **Labels:** security
- **Source:** CODE_QUALITY_ASSESSMENT.md - Security section

#### 3. Add controller unit tests
- **Priority:** medium
- **Labels:** testing, tech-debt
- **Source:** CODE_QUALITY_ASSESSMENT.md - Testability section

---

**Options:**
- `--dry-run` mode: No issues will be created
- Continue to create all issues? [Y/n]
```

### Step 3: Create Issues

For each item, create a GitHub issue using `gh` CLI:

#### From Queue Items

```bash
gh issue create \
  --title "Add rate limiting to login endpoint" \
  --body "$(cat <<'EOF'
## Background

Discovered during implementation of Issue #34 (Phase 2).

## Description

No rate limiting on auth endpoints. Could be vulnerable to brute force attacks.

## Suggested Priority

Medium

## Source

- Queue item: q-001
- Original issue: #34
- Phase: 2

---
*Created via Tiki /tiki:create-issues from queue*
EOF
)" \
  --label "security" \
  --label "enhancement"
```

#### From Assessment Findings

```bash
gh issue create \
  --title "Security: Missing CSRF Protection" \
  --body "$(cat <<'EOF'
## Finding

POST actions lack ValidateAntiForgeryToken attribute.

## Affected Files

- `Controllers/UserController.cs`
- `Controllers/OrderController.cs`

## Recommendation

Add `[ValidateAntiForgeryToken]` to all POST actions.

## Assessment Details

- **Category:** Security
- **Severity:** Critical
- **Assessment Date:** 2026-01-10

---
*Created via Tiki /tiki:create-issues from CODE_QUALITY_ASSESSMENT.md*
EOF
)" \
  --label "security" \
  --label "high-priority"
```

### Step 4: Apply Labels

When `--labels` is specified, auto-apply labels based on category:

| Category | Labels |
|----------|--------|
| Security | `security` |
| Testing | `testing`, `tech-debt` |
| Architecture | `architecture`, `refactor` |
| Documentation | `documentation` |
| Error Handling | `bug`, `reliability` |
| Dependencies | `dependencies`, `maintenance` |
| Code Quality | `tech-debt`, `cleanup` |

### Step 5: Apply Priority

When `--priority` is specified, add priority labels:

| Priority | Label |
|----------|-------|
| `critical` | `critical`, `P0` |
| `high` | `high-priority`, `P1` |
| `medium` | `medium-priority`, `P2` |
| `low` | `low-priority`, `P3` |

```bash
# Example with priority
gh issue create \
  --title "Add rate limiting" \
  --body "..." \
  --label "security" \
  --label "high-priority"
```

### Step 6: Update Queue (if from queue)

After creating issues from queue, update `.tiki/queue/pending.json`:

```json
{
  "items": [],
  "processed": [
    {
      "id": "q-001",
      "action": "created-issue",
      "issueNumber": 45,
      "processedAt": "2026-01-10T14:00:00Z"
    },
    {
      "id": "q-002",
      "action": "created-issue",
      "issueNumber": 46,
      "processedAt": "2026-01-10T14:00:01Z"
    }
  ]
}
```

### Step 7: Display Summary

```
## Create Issues Complete

**Created 5 issues:**

| # | Title | Labels | Priority |
|---|-------|--------|----------|
| #45 | Add rate limiting to login endpoint | security, enhancement | medium |
| #46 | Missing CSRF Protection | security | critical |
| #47 | Add controller unit tests | testing, tech-debt | medium |
| #48 | Remove dead code files | tech-debt, cleanup | low |
| #49 | Update deprecated packages | dependencies | medium |

**Queue status:** Cleared (3 items processed)

**Next steps:**
- View issues: `gh issue list`
- Prioritize: `gh issue edit #45 --add-label "P1"`
- Plan an issue: `/tiki:plan-issue 45`
```

## Options Reference

| Option | Description |
|--------|-------------|
| `--from-queue` | Create issues from `.tiki/queue/pending.json` |
| `--from-assessment` | Create issues from `docs/CODE_QUALITY_ASSESSMENT.md` |
| `--labels` | Auto-apply labels based on category |
| `--priority <level>` | Set priority: `critical`, `high`, `medium`, `low` |
| `--dry-run` | Preview issues without creating them |

## Examples

### Example 1: Create Issues from Queue

```
User: /tiki:create-issues --from-queue

Claude: ## Create Issues Preview

**Source:** Queue (2 items)

### Issues to Create

1. **Add rate limiting to login endpoint**
   - Priority: medium
   - Labels: security, enhancement

2. **Consider adding refresh tokens**
   - Priority: low
   - Labels: enhancement

Creating issues...

Created #45: Add rate limiting to login endpoint
Created #46: Consider adding refresh tokens

2 issues created. Queue cleared.
```

### Example 2: Create Issues from Assessment with Labels

```
User: /tiki:create-issues --from-assessment --labels --priority high

Claude: ## Create Issues Preview

**Source:** CODE_QUALITY_ASSESSMENT.md (4 findings)

### Issues to Create

1. **Security: Missing CSRF Protection** [critical]
2. **Testing: Add controller unit tests** [high]
3. **Tech Debt: Remove duplicate code** [medium]
4. **Documentation: Add API documentation** [low]

Creating issues with labels and high priority...

Created #50: Security: Missing CSRF Protection [security, critical]
Created #51: Testing: Add controller unit tests [testing, high-priority]
Created #52: Tech Debt: Remove duplicate code [tech-debt, high-priority]
Created #53: Documentation: Add API documentation [documentation, high-priority]

4 issues created.
```

### Example 3: Dry Run Preview

```
User: /tiki:create-issues --from-queue --dry-run

Claude: ## Create Issues Preview (Dry Run)

**Source:** Queue (3 items)

### Would Create

1. **Add rate limiting to login endpoint**
   ```
   gh issue create --title "Add rate limiting to login endpoint" \
     --body "..." --label "security" --label "enhancement"
   ```

2. **Password strength validation needed**
   ```
   gh issue create --title "Password strength validation needed" \
     --body "..." --label "security"
   ```

3. **Consider extracting auth service**
   ```
   gh issue create --title "Consider extracting auth service" \
     --body "..." --label "architecture" --label "refactor"
   ```

**Dry run complete.** No issues created.
Run without `--dry-run` to create these issues.
```

## Assessment File Format

The create-issues skill expects `CODE_QUALITY_ASSESSMENT.md` to have structured findings:

```markdown
# Code Quality Assessment

## Summary
Overall Score: 72/100

## Findings

### Security (Score: 65/100)

#### Critical
- **Finding Title** - Brief description
  - Files: `path/to/file.cs`
  - Recommendation: What to do

#### High Priority
- **Finding Title** - Brief description
  - Files: `path/to/file.cs`
  - Recommendation: What to do

### Testing (Score: 45/100)

#### High Priority
- **Finding Title** - Brief description
  - Recommendation: What to do
```

## Notes

- Issues created include source tracking (queue item ID or assessment section)
- Queue is updated after successful issue creation
- Use `--dry-run` to preview before creating
- Labels are applied based on category mapping if `--labels` is specified
- Priority labels override category-based priority labels
- The `gh` CLI must be authenticated (`gh auth status`)
