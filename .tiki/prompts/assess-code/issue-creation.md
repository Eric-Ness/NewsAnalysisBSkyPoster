# Issue Creation from Assessment

Create GitHub issues from assessment findings using `/tiki:create-issues`.

## Severity-Based Grouping

Present findings grouped by severity:

```
Create issues from assessment findings?

Critical issues ({count}):
- [ ] #{n}: {category} - {brief description}

High priority issues ({count}):
- [ ] #{n}: {category} - {brief description}

Medium priority issues ({count}):
- [ ] #{n}: {category} - {brief description}

Low priority issues ({count}):
- [ ] #{n}: {category} - {brief description}

Create all? [Yes/Select/No]
```

## Issue Format

Each created issue should include:
- **Title**: `[{Category}] {Brief description}`
- **Body**:
  - Location (file and line if available)
  - Current problem
  - Recommended fix
  - Assessment reference

## Selection Prompt

If user selects "Select":
1. Show numbered list of all issues
2. Accept comma-separated numbers or ranges
3. Create only selected issues

## Integration Command

After assessment, prompt:
```
Create GitHub issues from findings? `/tiki:create-issues --from-assessment`
```
