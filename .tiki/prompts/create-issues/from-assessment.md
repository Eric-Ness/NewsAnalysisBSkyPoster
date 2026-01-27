# Creating Issues from Code Assessment

## Assessment File Format

CODE_QUALITY_ASSESSMENT.md contains:
- **Summary section** with overall scores
- **Category sections** (Architecture, Code Quality, Testing, etc.)
- **Findings** with severity levels and recommendations

## Parsing Assessment Findings

1. **Locate findings sections** - Look for headers like "Issues Found", "Recommendations", or bullet lists under category headings
2. **Extract severity** - Map terms: "critical" -> P0, "high" -> P1, "medium" -> P2, "low" -> P3
3. **Capture context** - Include file paths, line references, and specific code patterns mentioned

## Category to Label Mapping

| Assessment Category | GitHub Labels |
|---------------------|---------------|
| Architecture | `architecture`, `refactor` |
| Code Quality | `code-quality`, `tech-debt` |
| Testing | `testing`, `coverage` |
| Documentation | `documentation` |
| Security | `security`, `priority:high` |
| Performance | `performance` |
| Dependencies | `dependencies`, `maintenance` |

## Issue Creation from Findings

For each finding:
1. **Title**: `[Category] Brief description of issue`
2. **Body**: Include the finding text, affected files, and recommended fix
3. **Labels**: Apply mapped labels plus severity label
4. **Priority**: Derive from severity level

## Batch Processing

When multiple findings exist:
- Group related findings into single issues where logical
- Create separate issues for unrelated problems
- Link issues that have dependencies
