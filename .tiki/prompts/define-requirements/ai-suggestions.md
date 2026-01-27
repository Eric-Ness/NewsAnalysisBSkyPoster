# Codebase Analysis for AI Suggestions

**Load condition:** Generating requirements from codebase analysis (not using --from-issues flag)

## Purpose

Scan the codebase to detect implemented features and map them to potential requirements.

---

## Detection Patterns

### Commands Detection

| Pattern Type | Glob/Search |
|-------------|-------------|
| Claude Code commands | `.claude/commands/**/*.md` |
| CLI commands (TS/JS) | `**/commands/*.ts`, `**/commands/*.js` |
| CLI commands (Go) | `**/cmd/*.go` |
| npm scripts | Read `package.json` -> extract "scripts" |

Output: `{"commands": [{"file": "path", "name": "name", "type": "type"}]}`

### API Endpoints Detection

| Framework | Grep Pattern | File Types |
|-----------|-------------|------------|
| Express/Koa | `app\.(get\|post\|put\|delete\|patch)\s*\(` | ts, js |
| NestJS | `@(Get\|Post\|Put\|Delete\|Patch)\s*\(` | ts |
| FastAPI | `@(app\|router)\.(get\|post\|put\|delete)\s*\(` | py |
| Go HTTP | `HandleFunc\s*\(\|Handle\s*\(` | go |
| Next.js | Glob: `**/pages/api/**/*.ts`, `**/app/api/**/route.ts` | - |

Output: `{"apiEndpoints": [{"method": "GET", "path": "/api/...", "file": "path", "line": 15}]}`

### Test Coverage Detection

| Pattern Type | Glob |
|-------------|------|
| JS/TS tests | `**/*.test.ts`, `**/*.spec.ts`, `**/*.test.js`, `**/*.spec.js` |
| Jest directories | `**/__tests__/**/*.ts`, `**/__tests__/**/*.js` |
| Python tests | `**/test/**/*.py` |
| Go tests | `**/*_test.go` |
| Coverage reports | `coverage/coverage-summary.json`, `coverage/lcov-report/index.html` |

Group test files by directory to identify well-tested vs under-tested areas.

### Auth Detection

| Feature | Grep Pattern (case-insensitive where noted) |
|---------|---------------------------------------------|
| Auth keywords | `(auth\|authenticate\|authorization)` -i |
| Login/logout | `(login\|logout\|signIn\|signOut\|session)` -i |
| JWT/token | `(jwt\|token\|bearer)` -i |
| Middleware | `(requireAuth\|isAuthenticated\|authMiddleware\|@Authorized)` |
| OAuth | `(oauth\|passport\|provider)` -i |
| Permissions | `(permission\|role\|access\|canAccess)` -i |

Output: `{"authFeatures": {"hasAuth": true, "patterns": ["jwt"], "endpoints": [], "middleware": [], "roles": []}}`

---

## Building the Functionality Map

Combine all detected patterns into:

```json
{
  "functionalityMap": {
    "implemented": [{"category": "Name", "features": [{"name": "Feature", "evidence": ["file:line"], "tested": true}]}],
    "pending": [{"category": "From Issues", "features": [{"name": "Feature", "source": "Issue #N", "labels": []}]}],
    "metadata": {"analyzedAt": "ISO", "totalImplemented": 0, "totalPending": 0, "totalTested": 0}
  }
}
```

Display as:

```
## Codebase Analysis Complete
### Implemented Functionality
| Category | Features | Tested |
|----------|----------|--------|
| Auth | 3 features | 2/3 (67%) |

### Coverage Gaps
- [Feature]: Implemented but not tested
```

---

## Issue-to-Functionality Matching

For each open issue:

1. Extract keywords from title/body
2. Search `functionalityMap.implemented` for matches
3. Classify by confidence:

| Confidence | Status | Action |
|------------|--------|--------|
| >70% | potentiallyImplemented | Flag for review |
| 50-70% | enhancement | Link to related feature |
| <50% | new | Add as new requirement |

Output:
```json
{"issueAnalysis": [{"issue": {"number": 42, "title": "..."}, "status": "new|potentiallyImplemented|enhancement", "matchedFeatures": [], "confidence": 0.0, "recommendation": "..."}]}
```

Display as:

```
## Issue-to-Functionality Analysis
### Potentially Already Implemented (Review Needed)
| Issue | Title | Matched Feature | Confidence |
|-------|-------|-----------------|------------|

### Enhancements to Existing Features
| Issue | Title | Related Feature | Confidence |
|-------|-------|-----------------|------------|

### New Functionality
| Issue | Title | Suggested Category |
|-------|-------|-------------------|
```
