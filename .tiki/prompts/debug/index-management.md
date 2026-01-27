# Index Management

Internal operations for maintaining `.tiki/debug/index.json`.

## Index Schema

```json
{
  "version": "1.0",
  "generatedAt": "<ISO timestamp>",
  "sessions": [{
    "id": "issue-42-api-error",
    "filename": "issue-42-api-error.md",
    "issue": 42,
    "title": "API returns 500 error",
    "type": "issue-linked|untracked",
    "status": "active|resolved|abandoned",
    "createdAt": "<ISO>",
    "resolvedAt": "<ISO>",
    "rootCause": "summary",
    "keywords": ["api", "error"],
    "errorPatterns": ["ECONNREFUSED"],
    "affectedFiles": ["src/api.js"],
    "solution": "summary",
    "archived": false
  }]
}
```

## Initialization

If no index exists:
```bash
echo '{"version":"1.0","generatedAt":"'$(date -Iseconds)'","sessions":[]}' > .tiki/debug/index.json
```

## Update Triggers

Update index after:
- Creating new session
- Resolving session
- Abandoning session
- Archiving session

## Update Procedure

1. Read index
2. Extract from session doc: status, dates, root cause, solution
3. Extract keywords from Symptoms (errors, codes, terms)
4. Extract error patterns from Error Output
5. Extract affected files from code references
6. Update or add session entry
7. Write index

## Keyword Extraction

| Source | Extract |
|--------|---------|
| Symptoms section | Error codes, status codes, component names |
| Root Cause section | Technical terms, library names |

**Normalization:** lowercase, remove common words (the, a, is, etc.), dedupe

## Error Pattern Extraction

Look for in Error Output/Symptoms:
- Stack trace patterns (`at Module._compile`)
- Error codes (`ECONNREFUSED`, `ENOENT`)
- HTTP status codes (`500`, `404`)
- Exception names (`TypeError`, `NullPointerException`)

## Affected Files Extraction

Parse session document for:
- File paths in code blocks
- References like `src/api.js:42`
- Files modified in Solution Applied section

## Validation

If index corrupted or out of sync:
1. Scan all `.md` files in `.tiki/debug/`
2. Parse each for Session Info table
3. Rebuild sessions array
4. Write fresh index
