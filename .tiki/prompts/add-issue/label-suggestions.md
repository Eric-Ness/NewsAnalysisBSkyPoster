# Label Suggestions

## Issue Type Detection

Analyze the issue title and description to detect the type:

| Keywords | Type | Suggested Labels |
|----------|------|------------------|
| add, create, new, implement | feature | `enhancement`, `feature` |
| fix, bug, broken, error, crash | bug | `bug`, `defect` |
| update, improve, enhance, optimize | enhancement | `enhancement`, `improvement` |
| docs, documentation, readme, guide | documentation | `documentation`, `docs` |
| refactor, cleanup, reorganize | refactor | `refactor`, `tech-debt` |
| test, testing, coverage | testing | `testing`, `test` |
| security, vulnerability, auth | security | `security`, `priority-high` |
| performance, slow, optimize | performance | `performance`, `enhancement` |

## Checking Repository Labels

Before suggesting labels, verify which labels exist in the repository:

```bash
gh label list --json name,description
```

Only suggest labels that exist in the repository. If a suggested label doesn't exist, either:
1. Skip that label suggestion
2. Suggest creating the label if appropriate

## Label Selection Guidelines

1. **Primary label**: Always suggest one primary type label (bug, enhancement, etc.)
2. **Priority labels**: Suggest priority if urgency is indicated (priority-high, priority-low)
3. **Area labels**: Suggest component/area labels if the repo uses them
4. **Limit count**: Suggest 1-3 labels maximum to avoid over-labeling

## Presenting Suggestions

Format label suggestions as:
```
Suggested labels: `enhancement`, `documentation`
```

Ask user to confirm or modify before applying labels to the issue.
