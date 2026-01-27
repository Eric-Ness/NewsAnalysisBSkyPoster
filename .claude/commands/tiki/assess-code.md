---
type: prompt
name: tiki:assess-code
description: Comprehensive codebase health assessment with scoring across multiple dimensions. Use when evaluating code quality, identifying issues, or tracking improvement over time.
allowed-tools: Read, Write, Bash, Glob, Grep, Task
argument-hint: [path] [--quick] [--dimension <name>] [--create-issues]
---

# Assess Code

Comprehensive codebase health assessment that generates a scored report.

## Usage

```
/tiki:assess-code
/tiki:assess-code src/
/tiki:assess-code --quick
/tiki:assess-code --dimension security
/tiki:assess-code --create-issues
```

## Instructions

### Step 1: Determine Scope

If path provided, assess that path only. Otherwise, assess entire codebase.

```
Assessing: src/
Excluding: node_modules, .git, dist, coverage
```

### Step 2: Run Assessment Dimensions

Assess each dimension and calculate scores (0-100):

---

#### Dimension 1: Architecture & Structure (15% weight)

**What to evaluate:**

```
# Directory depth and organization
find . -type d -maxdepth 5 | wc -l

# Separation of concerns
Glob: src/**/*.ts
# Check for mixed responsibilities (UI logic in data layer, etc.)

# Circular dependencies
# Check import patterns for cycles

# File sizes
find . -name "*.ts" -exec wc -l {} + | sort -rn | head -20
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | Clear layering, no circular deps, consistent naming, < 300 LOC per file |
| 70-89 | Good structure, minor inconsistencies, few large files |
| 50-69 | Mixed organization, some circular deps, unclear boundaries |
| 30-49 | Poor separation, many large files, unclear architecture |
| 0-29 | No clear structure, monolithic files, chaotic organization |

**Output findings:**

```json
{
  "dimension": "architecture",
  "score": 75,
  "findings": [
    {"severity": "medium", "issue": "src/legacy.ts is 847 lines - split recommended", "file": "src/legacy.ts"},
    {"severity": "low", "issue": "Circular dependency: user.ts <-> team.ts", "files": ["src/user.ts", "src/team.ts"]}
  ]
}
```

---

#### Dimension 2: Code Quality & Maintainability (15% weight)

**What to evaluate:**

```
# Code duplication (similar patterns)
Grep: "// TODO|// FIXME|// HACK"

# Dead code indicators
Grep: "// @deprecated|// unused|// remove"

# Complexity indicators (deep nesting)
Grep: "^\s{20,}" --type ts

# Magic numbers/strings
Grep: "\b\d{3,}\b" --type ts  # Numbers > 99

# Console statements in production
Grep: "console\.(log|debug|info|warn)" --type ts --glob "!**/*.test.*"
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | Clean code, no duplication, clear naming, well-documented |
| 70-89 | Minor issues, few TODOs, acceptable complexity |
| 50-69 | Some duplication, moderate complexity, scattered TODOs |
| 30-49 | Significant duplication, complex code, many TODOs |
| 0-29 | Unmaintainable, heavy duplication, cryptic code |

---

#### Dimension 3: Testability (15% weight)

**What to evaluate:**

```
# Test file presence
Glob: **/*.test.ts, **/*.spec.ts, **/__tests__/**

# Coverage (if available)
cat coverage/coverage-summary.json 2>/dev/null

# Test patterns
Grep: "(describe|it|test)\(" --type ts

# Mocking patterns
Grep: "(jest\.mock|vi\.mock|sinon)" --type ts
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | >80% coverage, comprehensive tests, good patterns |
| 70-89 | 60-80% coverage, key paths tested |
| 50-69 | 40-60% coverage, basic tests exist |
| 30-49 | 20-40% coverage, sparse testing |
| 0-29 | <20% coverage or no tests |

---

#### Dimension 4: Security (20% weight)

**What to evaluate:**

```
# Hardcoded secrets
Grep: "(password|secret|apikey|api_key|token)\s*[:=]" -i --type ts

# SQL injection risks
Grep: "query\s*\(" --type ts  # Raw queries

# XSS vulnerabilities
Grep: "dangerouslySetInnerHTML|innerHTML" --type ts

# Insecure patterns
Grep: "(eval|Function\()" --type ts

# Auth patterns
Grep: "@Authorized|requireAuth|isAuthenticated" --type ts

# Input validation
Grep: "(validate|sanitize|escape)" --type ts
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | No vulnerabilities, proper auth, input validation, secure patterns |
| 70-89 | Minor concerns, auth in place, mostly validated inputs |
| 50-69 | Some vulnerabilities, incomplete validation |
| 30-49 | Security gaps, missing auth on routes, injection risks |
| 0-29 | Critical vulnerabilities, secrets in code, no validation |

---

#### Dimension 5: Error Handling (10% weight)

**What to evaluate:**

```
# Generic catch blocks
Grep: "catch\s*\(\s*(e|err|error)?\s*\)" --type ts

# Empty catches
Grep: "catch\s*\([^)]*\)\s*\{\s*\}" --type ts

# Error logging
Grep: "(logger|console)\.(error|warn)" --type ts

# Custom error types
Grep: "extends Error" --type ts

# Try-catch coverage
Grep: "try\s*\{" --type ts
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | Specific error types, proper logging, graceful degradation |
| 70-89 | Good error handling, some generic catches |
| 50-69 | Basic try-catch, mixed logging, some empty catches |
| 30-49 | Many generic catches, poor logging |
| 0-29 | No error handling, silent failures |

---

#### Dimension 6: Documentation (10% weight)

**What to evaluate:**

```
# README presence and quality
Read: README.md

# API documentation
Grep: "@api|@swagger|@openapi" --type ts

# JSDoc comments
Grep: "/\*\*" --type ts

# Inline comments ratio
# Count comments vs code lines

# Type definitions
Glob: **/*.d.ts, **/types.ts, **/types/*.ts
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | Comprehensive README, API docs, JSDoc on public APIs |
| 70-89 | Good README, some API docs, key functions documented |
| 50-69 | Basic README, scattered comments |
| 30-49 | Minimal README, few comments |
| 0-29 | No README or outdated, no documentation |

---

#### Dimension 7: Dependencies & Modernization (10% weight)

**What to evaluate:**

```
# Outdated packages
npm outdated 2>/dev/null | wc -l

# Security vulnerabilities
npm audit --json 2>/dev/null | head -100

# Deprecated packages
Grep: "deprecated" package-lock.json

# Framework versions
cat package.json | grep -E "(react|vue|angular|express|next)"
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | All current, no vulnerabilities, modern stack |
| 70-89 | Minor updates available, no critical vulnerabilities |
| 50-69 | Some outdated deps, low-severity vulnerabilities |
| 30-49 | Many outdated, some high-severity vulnerabilities |
| 0-29 | Severely outdated, critical vulnerabilities |

---

#### Dimension 8: Interfaces & Abstractions (5% weight)

**What to evaluate:**

```
# Interface definitions
Grep: "^(export\s+)?interface\s+" --type ts

# Abstract classes
Grep: "abstract class" --type ts

# Dependency injection patterns
Grep: "@Injectable|@Inject|useContext" --type ts

# Coupling (direct instantiation vs injection)
Grep: "new\s+\w+Service" --type ts
```

**Scoring criteria:**

| Score | Criteria |
|-------|----------|
| 90-100 | Well-defined interfaces, DI used, loose coupling |
| 70-89 | Good abstractions, some direct coupling |
| 50-69 | Basic interfaces, mixed patterns |
| 30-49 | Few interfaces, tight coupling |
| 0-29 | No abstractions, everything concrete |

---

### Step 3: Calculate Overall Score

Apply weights to dimension scores:

```javascript
const weights = {
  architecture: 0.15,
  codeQuality: 0.15,
  testability: 0.15,
  security: 0.20,
  errorHandling: 0.10,
  documentation: 0.10,
  dependencies: 0.10,
  interfaces: 0.05
};

let overall = 0;
for (const [dim, weight] of Object.entries(weights)) {
  overall += scores[dim] * weight;
}
```

### Step 4: Generate Report

Create `docs/CODE_QUALITY_ASSESSMENT.md`:

```markdown
# Code Quality Assessment

> Generated by Tiki on 2026-01-10

## Overall Score: 72/100

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Architecture & Structure | 75 | 15% | 11.25 |
| Code Quality | 70 | 15% | 10.50 |
| Testability | 65 | 15% | 9.75 |
| Security | 80 | 20% | 16.00 |
| Error Handling | 68 | 10% | 6.80 |
| Documentation | 60 | 10% | 6.00 |
| Dependencies | 85 | 10% | 8.50 |
| Interfaces | 65 | 5% | 3.25 |

## Score History

| Date | Score | Change | Notes |
|------|-------|--------|-------|
| 2026-01-10 | 72 | -- | Initial assessment |

## Detailed Findings

### Critical (Must Fix)

| Issue | Location | Recommendation |
|-------|----------|----------------|
| Hardcoded API key | src/config.ts:23 | Move to environment variable |
| SQL injection risk | src/db/queries.ts:45 | Use parameterized queries |

### High Priority

| Issue | Location | Recommendation |
|-------|----------|----------------|
| No input validation | src/api/users.ts | Add Zod validation |
| Missing auth | src/api/admin.ts | Add authorization middleware |
| Empty catch block | src/services/email.ts:89 | Log error and handle |

### Medium Priority

| Issue | Location | Recommendation |
|-------|----------|----------------|
| Large file | src/legacy.ts (847 lines) | Split into modules |
| Console.log | src/api/debug.ts | Remove or use logger |
| Generic catch | 15 locations | Use specific error types |

### Low Priority

| Issue | Location | Recommendation |
|-------|----------|----------------|
| TODO comments | 23 locations | Review and resolve |
| Missing JSDoc | src/utils/*.ts | Add documentation |
| Magic numbers | src/constants.ts | Extract to named constants |

## Dimension Details

### Architecture & Structure (75/100)

**Strengths:**
- Clear separation between API, services, and data layers
- Consistent file naming conventions
- Reasonable directory structure

**Weaknesses:**
- src/legacy.ts is too large (847 lines)
- Circular dependency between user.ts and team.ts
- Some mixed concerns in utility files

**Recommendations:**
1. Split legacy.ts into domain-specific modules
2. Extract shared types to break circular dependency
3. Review utils/ for proper categorization

### Security (80/100)

**Strengths:**
- JWT authentication implemented
- Most routes properly protected
- Input validation on critical paths

**Weaknesses:**
- One hardcoded API key found
- File upload lacks type validation
- Some admin routes missing authorization

**Recommendations:**
1. Move API key to environment variables
2. Add file type and size validation to uploads
3. Add @Authorized decorator to admin routes

[... additional dimension details ...]

## Recommendations Summary

### Immediate Actions
1. Fix hardcoded API key in config.ts
2. Add parameterized queries to prevent SQL injection
3. Validate file uploads in upload.ts

### Short-term Improvements
1. Increase test coverage from 45% to 60%
2. Add authorization to admin routes
3. Split legacy.ts into smaller modules

### Long-term Goals
1. Achieve 80% test coverage
2. Add comprehensive API documentation
3. Implement structured logging
```

### Step 5: Update Score History

If previous assessment exists, append to history:

```markdown
| Date | Score | Change | Notes |
|------|-------|--------|-------|
| 2026-01-10 | 72 | +5 | Added auth to admin routes |
| 2026-01-08 | 67 | +3 | Fixed SQL injection |
| 2026-01-05 | 64 | -- | Initial assessment |
```

### Step 6: Display Summary

```
## Code Quality Assessment Complete

**Overall Score: 72/100** (+5 from last assessment)

### Dimension Scores
Architecture:    ████████░░ 75
Code Quality:    ███████░░░ 70
Testability:     ██████░░░░ 65
Security:        ████████░░ 80
Error Handling:  ██████░░░░ 68
Documentation:   ██████░░░░ 60
Dependencies:    ████████░░ 85
Interfaces:      ██████░░░░ 65

### Top Issues
- [CRITICAL] Hardcoded API key in config.ts
- [HIGH] SQL injection risk in queries.ts
- [HIGH] Missing auth on admin routes

### Report Location
docs/CODE_QUALITY_ASSESSMENT.md

---
Create GitHub issues from findings? `/tiki:create-issues --from-assessment`
Re-run specific dimension? `/tiki:assess-code --dimension security`
```

## Quick Mode

With `--quick` flag, run abbreviated checks:

```
Quick Assessment (5 dimensions only)

Security:     ████████░░ 80
Testability:  ██████░░░░ 65
Code Quality: ███████░░░ 70
Architecture: ████████░░ 75
Dependencies: ████████░░ 85

Estimated Overall: 74/100

Run full assessment for detailed report: `/tiki:assess-code`
```

## Single Dimension Mode

With `--dimension <name>`:

```
/tiki:assess-code --dimension security
```

Runs only that dimension with extra detail:

```
## Security Assessment (Detailed)

**Score: 80/100**

### Checks Performed

| Check | Status | Details |
|-------|--------|---------|
| Hardcoded secrets | WARN | 1 found in config.ts |
| SQL injection | PASS | Parameterized queries used |
| XSS prevention | PASS | No dangerouslySetInnerHTML |
| CSRF protection | PASS | Tokens validated |
| Auth coverage | WARN | 3 routes missing auth |
| Input validation | WARN | Incomplete on 5 endpoints |
| Dependency vulns | PASS | No known vulnerabilities |

### Findings

[Detailed list specific to security]
```

## Integration with Create-Issues

With `--create-issues`:

```
Create issues from assessment findings?

Critical issues (2):
- [ ] #1: Security - Move API key to environment variable
- [ ] #2: Security - Fix SQL injection in queries.ts

High priority issues (3):
- [ ] #3: Security - Add auth to admin routes
- [ ] #4: Testing - Add validation tests
- [ ] #5: Architecture - Split legacy.ts

Create all? [Yes/Select/No]
```

## Notes

- Full assessment may take 2-5 minutes depending on codebase size
- Use `--quick` for faster, less detailed results
- Score history is tracked in the report file
- Integration with `/tiki:create-issues` to action findings
- Reports are stored in `docs/` by default
- Can be run on specific directories for focused assessment
