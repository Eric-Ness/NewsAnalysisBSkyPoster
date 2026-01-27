# Issue Generation

Convert requirements into GitHub issues ready for `/tiki:yolo`.

## Overview

Each requirement (or logical grouping) becomes a GitHub issue with:

- Clear title
- Structured body with acceptance criteria
- Labels based on category
- Dependency references

## Grouping Strategy

Not every requirement needs its own issue. Group when:

- Requirements are tightly coupled (same feature area)
- One can't be implemented without another
- They share the same files/components

Keep separate when:

- Requirements are independently valuable
- Different complexity levels
- Could be parallelized

## Issue Template

```markdown
## Summary

[1-2 sentence description of what this issue accomplishes]

## Requirements

- [ ] **[REQ-ID]**: [requirement description]
- [ ] **[REQ-ID]**: [requirement description]

## Acceptance Criteria

- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

## Dependencies

[If any]
- Depends on #[number]: [brief reason]

## Notes

[Any context from research, constraints, or decisions]

---

*Generated from requirements by `/tiki:new-project`*
```

## Labels

Apply labels based on category:

| Category | Label |
| -------- | ----- |
| AUTH | `auth` |
| CORE | `core` |
| DATA | `data` |
| UI | `ui` |
| INT | `integration` |
| SEC | `security` |
| PERF | `performance` |
| DOC | `documentation` |

Also apply:

- `v1` for v1 requirements
- `enhancement` for new features

## Create Issues

Use GitHub CLI:

```bash
gh issue create \
  --title "[Title]" \
  --body "[Body]" \
  --label "v1,core"
```

Capture issue number for dependency linking.

## Dependency Handling

After creating all issues, update bodies with actual issue numbers:

1. Create all issues first (capture numbers)
2. For issues with dependencies, edit to add `Depends on #N`

```bash
gh issue edit [number] --body "[updated body with dependencies]"
```

## Milestone (Optional)

Ask user if they want a v1 milestone:

```text
header: "Milestone"
question: "Create a v1 milestone and assign issues?"
options:
  - "Create milestone" — Group issues under v1 milestone
  - "Skip" — No milestone needed
```

If yes:

```bash
gh api repos/{owner}/{repo}/milestones -f title="v1" -f state="open"
gh issue edit [number] --milestone "v1"
```

## Output Summary

After creating issues, display:

```text
## Issues Created

| # | Title | Requirements | Labels |
| - | ----- | ------------ | ------ |
| 1 | Setup authentication | AUTH-01, AUTH-02 | auth, v1 |
| 2 | Create post functionality | CORE-01, CORE-02 | core, v1 |
| 3 | User profile page | UI-01 | ui, v1 |

**Total:** [N] issues created
**Milestone:** v1 (if created)

## Dependency Graph

#1 (auth) ← #2 (posts depend on auth)
#1 (auth) ← #3 (profile depends on auth)

## Next Steps

- `/tiki:pick-issue` — See recommended starting point
- `/tiki:yolo 1` — Start with issue #1
```

## Update Requirements

After creating issues, update `.tiki/requirements.json` with linkedIssue:

```json
{
  "id": "AUTH-01",
  "description": "...",
  "status": "pending",
  "version": "v1",
  "linkedIssue": 1
}
```

## Error Handling

If issue creation fails:

- Display error message
- Offer: Retry / Skip this issue / Cancel remaining
- Track which issues were created vs failed
