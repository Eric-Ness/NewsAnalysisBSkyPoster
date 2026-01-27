# Requirements Linking

Map issues to requirements from `.tiki/requirements.json`.

## Suggestion Logic

Analyze issue title, body, and labels for keyword matches against requirement text.

```javascript
// Match keywords (>3 chars) from requirement text against issue content
// Sort by match count, return top 5 suggestions
```

## Single Issue Prompt

```text
### Requirements Mapping

Issue #{number}: {title}

Suggested requirements:
- {REQ-ID}: {description}

1. **Accept** - Map to suggestions
2. **Edit** - Choose different requirements
3. **Skip** - No requirements for this issue
4. **View all** - See all available requirements

Enter choice:
```

## Edit Flow

Display requirements grouped by category:

```text
| ID | Requirement | Category |
|----|-------------|----------|
```

Prompt: Enter requirement IDs (comma-separated) or "none"

## Store Mapping

Add `requirements` array to issue entry in release file.

## No Suggestions Found

```text
No requirement suggestions found.

1. Enter requirements manually
2. Skip - No requirements
3. View all requirements
```
