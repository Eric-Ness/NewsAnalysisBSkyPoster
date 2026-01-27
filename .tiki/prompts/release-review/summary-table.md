# Summary Table Format

Template for displaying final release review summary.

## Summary Structure

```text
## Release Review Complete: {version}

### Results

| Issue | Title | Verdict | Concerns | Comment |
|-------|-------|---------|----------|---------|
| #{n} | {title} | CLEAN | 0 | - |
| #{n} | {title} | WARNINGS | {count} | Posted |
| #{n} | {title} | BLOCKED | {count} | Posted |

### Metrics

- **Total reviewed:** {N}
- **Clean:** {N} ({percentage}%)
- **Warnings:** {N}
- **Blocked:** {N}
- **Comments posted:** {N}

### Blocked Issues

{If any blocked issues, list them with brief description of blocking concern}

- #{number}: {title} - {blocking concern summary}

### Next Steps

{Based on results, provide appropriate guidance}

**If no blocked issues:**
- All issues reviewed and ready for planning
- Review posted comments for warning decisions
- Run `/tiki:release-yolo {version}` to execute

**If blocked issues exist:**
- Address blocked issues before planning:
  - #{number}: {action needed}
- Re-run `/tiki:release-review {version} --issue {numbers}` after resolution

---
*Review completed at {timestamp}*
```

## Verdict Indicators

- **CLEAN**: No concerns, ready to plan
- **WARNINGS**: Concerns addressed via deep-dive, decisions documented
- **BLOCKED**: Critical issues that need resolution before planning

## Formatting Guidelines

- Use consistent column widths in table
- Truncate long titles (max ~30 chars) with ellipsis
- Show most critical information first
- Make next steps actionable and specific
