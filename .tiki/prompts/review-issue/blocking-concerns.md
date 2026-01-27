# Blocking Concerns Handling

Guidelines for identifying and handling blocking issues that prevent planning.

## Blocking Triggers

Issues that MUST be resolved before planning:

| Trigger | Category | Rationale |
|---------|----------|-----------|
| Scope too large / should be split | `scope` | Creates bad plan with too many phases |
| Missing dependency on another issue | `dependency` | Work will be blocked anyway |
| Fundamentally wrong approach | `approach` | Don't waste time planning wrong thing |
| Critical missing information | `missing_info` | Can't plan without essential details |
| Security vulnerability in proposed approach | `security` | Must address before implementation |

## Scope Assessment

Issue should be split when:
- Combines multiple distinct features (e.g., auth AND authz)
- Would require more than 6-8 phases
- Has unrelated acceptance criteria
- Different parts could be released independently

## Dependency Detection

Check for:
- References to other issues ("depends on #X", "after #X")
- Prerequisites not yet implemented
- External service availability
- Required permissions or access not confirmed

## Wrong Approach Indicators

- Contradicts established patterns without justification
- Ignores existing infrastructure that solves the problem
- Proposes deprecated or unsuitable technology
- Violates architectural principles in CLAUDE.md

## Blocking Output Format

```json
{
  "severity": "blocking",
  "category": "scope|dependency|approach|missing_info|security",
  "message": "Clear description of the blocking issue",
  "resolution": "What needs to happen to unblock"
}
```

## Resolution Recommendations

For each blocking type:

### Scope Too Large
```text
- **[Scope]**: This issue should be split
  - Part 1: <description> (create as separate issue)
  - Part 2: <description> (create as separate issue)
  Resolution: Split into focused issues, then re-review
```

### Missing Dependency
```text
- **[Dependency]**: Depends on issue #X which is not complete
  Resolution: Complete #X first, or remove dependency
```

### Wrong Approach
```text
- **[Approach]**: Proposed approach conflicts with <reason>
  Resolution: Consider <alternative approach>
```

### Missing Information
```text
- **[Missing Info]**: <what is missing>
  Resolution: Clarify in issue body or comments
```

## Verdict Determination

```javascript
function determineVerdict(findings) {
  if (findings.some(f => f.severity === 'blocking')) {
    return 'blocked';
  }
  if (findings.some(f => f.severity === 'warning')) {
    return 'warnings';
  }
  return 'clean';
}
```

## YOLO Mode Behavior

When verdict is `blocked`:
- PAUSE execution
- Output structured REVIEW_RESULT with blocking concerns
- Require user intervention before continuing
