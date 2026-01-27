# Output Formats for Pick Issue

## Standard Output Format

```
## Pick Issue Analysis

Analyzed 12 open issues.

### Top Recommendations

#### 1. Issue #45: Add rate limiting to API
**Score: 7** | Labels: high-priority, security
- +3 preferred label (high-priority)
- +2 blocking label
- +2 unblocks: #48, #52

This is a good first pick because it's high priority and unblocks two other issues.

#### 2. Issue #42: Fix memory leak in worker process
**Score: 5** | Labels: bug, critical
- +3 preferred label (critical)
- +2 age (3 weeks old)

Long-standing critical bug that should be addressed.

#### 3. Issue #38: Update user profile endpoint
**Score: 3** | Labels: enhancement
- +2 age (4 weeks old)
- +1 enables: #50

Older issue with downstream benefits.

---

### Deferred (2 issues)
| Issue | Title | Why Deferred |
|-------|-------|--------------|
| #30 | Refactor config system | backlog label |
| #28 | Explore new framework | someday label |

### Blocked (1 issue)
| Issue | Title | Blocked By |
|-------|-------|------------|
| #48 | Add rate limit headers | #45 (open) |

---

**Suggested next step:**
/tiki:get-issue 45
```

## Error Handling

### No Issues Found

```
## Pick Issue Analysis

No open issues found in this repository.

To create a new issue:
gh issue create
```

### GitHub CLI Errors

```
## Pick Issue Analysis

Error: Unable to fetch issues from GitHub.

Possible causes:
- GitHub CLI (gh) is not installed
- Not authenticated: run `gh auth login`
- Not in a git repository
- No remote repository configured

Check your setup and try again.
```

### No Recommended Issues

```
## Pick Issue Analysis

Analyzed 5 open issues, but none are recommended:
- 3 issues are blocked by other open issues
- 2 issues are deferred (backlog)

### Blocked Issues
[list blocked issues with what blocks them]

### Deferred Issues
[list deferred issues]

Consider resolving blockers or promoting a deferred issue.
```
