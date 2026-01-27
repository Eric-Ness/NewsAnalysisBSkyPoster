# Risk Assessment Analysis

Perform thorough risk assessment when security, performance, or breaking change concerns are identified.

## Risk Categories

### Security Concerns
Evaluate for:
- Input validation vulnerabilities
- Authentication/authorization gaps
- Data exposure risks
- Injection vulnerabilities (SQL, XSS, etc.)
- Sensitive data handling
- API security (rate limiting, CORS)

**Severity:** Mark as `blocking` if security vulnerability in proposed approach.

### Performance Risk Evaluation
Analyze:
- Database query efficiency (N+1, missing indexes)
- Memory usage patterns
- Network call overhead
- Caching opportunities
- Pagination needs for large datasets
- Resource-intensive operations

**Severity:** Mark as `warning` unless critical performance impact expected.

### Breaking Changes Detection
Check for:
- API contract changes
- Database schema migrations
- Configuration changes
- Dependency version updates
- Interface/type changes
- Removal of existing functionality

**Severity:** Mark as `blocking` if breaking changes affect production users without migration path.

### Compatibility Concerns
Consider:
- Browser/platform compatibility
- Backward compatibility with existing data
- Integration with external services
- Version compatibility of dependencies

## Risk Severity Classification

| Risk Level | Criteria | Action |
|------------|----------|--------|
| **Critical** | Security vulnerability, data loss risk, production breaking | `blocking` |
| **High** | Significant performance impact, major breaking change | `blocking` or `warning` |
| **Medium** | Performance concern, minor breaking change with path | `warning` |
| **Low** | Potential issue, easy mitigation | `info` |

## Output Format

For each identified risk:

```json
{
  "severity": "blocking|warning|info",
  "category": "security|performance|breaking_change|compatibility",
  "message": "Clear description of the risk",
  "mitigation": "Suggested mitigation approach (optional)"
}
```

## Example Findings

```text
### Warnings (2)
- **[Performance]**: Database queries may cause N+1 problem with nested resources
- **[Security]**: Rate limiting not specified for public endpoint

### Blocking Concerns (1)
- **[Security]**: User input directly used in SQL query - injection vulnerability
```
