# Requirements Mapping Workflow

Map selected issues to requirements from `.tiki/requirements.json`.

## For Each Issue

### Suggest Requirements

Analyze issue title and body for keywords matching requirement categories.

Display suggestions:
```text
Issue #{number}: {title}
Labels: {labels}

Suggested requirements (based on keywords):
- {REQ-ID}: {description}

Map to these requirements?
1. Yes - Accept suggestions
2. Edit - Modify the mapping
3. Skip - No requirements for this issue
4. View all - See all available requirements
```

### Edit Mapping

If user selects "Edit":

Display all requirements grouped by category:
```text
| ID | Text | Category |
|----|------|----------|
```

Prompt for requirement IDs (comma-separated).

### View All Requirements

Display full requirements list, then return to mapping prompt.

## Store Mappings

```json
{
  "number": 42,
  "title": "Add dark mode toggle",
  "requirements": ["UI-01", "UI-02"]
}
```

## Batch Mode

For releases with many issues (>5), offer:

```text
## Batch Mapping Mode

1. Map each individually
2. Auto-map all - Accept suggested mappings
3. Skip all - No requirement mapping

Enter choice:
```

## No Matches Found

```text
Issue #{number}: {title}

No requirement suggestions found.

1. Enter requirements manually
2. Skip - No requirements for this issue
3. View all requirements
```
