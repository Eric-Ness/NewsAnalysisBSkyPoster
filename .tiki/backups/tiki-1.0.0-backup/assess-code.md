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
/tiki:assess-code                     # Full assessment
/tiki:assess-code src/                # Assess specific path
/tiki:assess-code --quick             # 5-dimension quick scan
/tiki:assess-code --dimension security  # Single dimension deep-dive
/tiki:assess-code --create-issues     # Create issues from findings
```

## Instructions

### Step 1: Determine Scope

If path provided, assess that path. Otherwise, assess entire codebase excluding node_modules, .git, dist, coverage.

### Step 2: Run Assessment Dimensions

Evaluate each dimension (0-100 score):

#### 1. Architecture & Structure (15%)

- Directory organization and depth
- Separation of concerns, layering
- Circular dependencies
- File sizes (<300 LOC ideal)

| 90-100 | Clear layering, no circular deps, <300 LOC/file |
| 70-89 | Good structure, minor issues |
| 50-69 | Mixed organization, some cycles |
| 30-49 | Poor separation, large files |
| 0-29 | Chaotic, monolithic |

#### 2. Code Quality (15%)

- Duplication, dead code
- Nesting depth, complexity
- Magic numbers/strings
- Console statements in production

| 90-100 | Clean, no duplication, clear naming |
| 70-89 | Minor issues, few TODOs |
| 50-69 | Some duplication, moderate complexity |
| 30-49 | Significant duplication, complex |
| 0-29 | Unmaintainable |

#### 3. Testability (15%)

- Test file coverage
- Coverage percentage
- Test patterns (describe/it/test)
- Mocking patterns

| 90-100 | >80% coverage, comprehensive |
| 70-89 | 60-80% coverage |
| 50-69 | 40-60% coverage |
| 30-49 | 20-40% coverage |
| 0-29 | <20% or no tests |

#### 4. Security (20%)

- Hardcoded secrets
- Injection risks (SQL, XSS)
- Insecure patterns (eval)
- Auth/validation coverage

| 90-100 | No vulnerabilities, proper auth |
| 70-89 | Minor concerns, mostly validated |
| 50-69 | Some vulnerabilities |
| 30-49 | Security gaps, missing auth |
| 0-29 | Critical vulnerabilities |

#### 5. Error Handling (10%)

- Generic vs specific catches
- Empty catch blocks
- Error logging
- Custom error types

| 90-100 | Specific types, proper logging |
| 70-89 | Good handling, some generic |
| 50-69 | Basic try-catch, mixed |
| 30-49 | Many generic catches |
| 0-29 | No handling, silent failures |

#### 6. Documentation (10%)

- README quality
- API docs, JSDoc
- Inline comments
- Type definitions

| 90-100 | Comprehensive docs |
| 70-89 | Good README, some API docs |
| 50-69 | Basic README |
| 30-49 | Minimal docs |
| 0-29 | No documentation |

#### 7. Dependencies (10%)

- Outdated packages
- Security vulnerabilities
- Deprecated deps
- Framework versions

| 90-100 | Current, no vulnerabilities |
| 70-89 | Minor updates, no critical |
| 50-69 | Some outdated, low severity |
| 30-49 | Many outdated, high severity |
| 0-29 | Severely outdated, critical |

#### 8. Interfaces (5%)

- Interface definitions
- Abstract classes
- Dependency injection
- Coupling patterns

| 90-100 | Well-defined, DI used |
| 70-89 | Good abstractions |
| 50-69 | Basic interfaces |
| 30-49 | Few interfaces |
| 0-29 | No abstractions |

### Step 3: Calculate Overall Score

```
overall = arch*0.15 + quality*0.15 + test*0.15 + security*0.20
        + errors*0.10 + docs*0.10 + deps*0.10 + interfaces*0.05
```

### Step 4: Generate Report

For full report format and template, read `.tiki/prompts/assess-code/detailed-findings.md`.

### Step 5: Historical Comparison

For score history tracking and trend display, read `.tiki/prompts/assess-code/historical-comparison.md`.

### Step 6: Display Summary

```
## Code Quality Assessment Complete

**Overall Score: 72/100** (+5 from last)

Architecture:    ████████░░ 75
Code Quality:    ███████░░░ 70
Testability:     ██████░░░░ 65
Security:        ████████░░ 80
Error Handling:  ██████░░░░ 68
Documentation:   ██████░░░░ 60
Dependencies:    ████████░░ 85
Interfaces:      ██████░░░░ 65

### Top Issues
- [CRITICAL] {issue}
- [HIGH] {issue}

Report: docs/CODE_QUALITY_ASSESSMENT.md
```

## Quick Mode

With `--quick`, assess only: Security, Testability, Code Quality, Architecture, Dependencies. Display scores and estimated overall.

## Single Dimension Mode

With `--dimension <name>`, run only that dimension with detailed checks table and expanded findings.

## Create Issues

With `--create-issues`, read `.tiki/prompts/assess-code/issue-creation.md` for issue creation workflow.

## Notes

- Full assessment takes 2-5 minutes
- Reports stored in `docs/`
- Can target specific directories
