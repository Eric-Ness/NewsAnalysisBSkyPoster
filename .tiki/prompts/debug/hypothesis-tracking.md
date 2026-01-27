# Hypothesis Tracking

Conditionally loaded during active debug session for hypothesis workflow management.

## Hypothesis States

| State | Meaning | Next Action |
|-------|---------|-------------|
| TESTING | Currently investigating | Execute test strategy |
| REJECTED | Disproven by evidence | Test next hypothesis |
| CONFIRMED | Root cause found | Go to resolution-recording.md |
| INCONCLUSIVE | Test not definitive | Try different approach or move on |

## Form Hypotheses

Generate 2-4 testable hypotheses based on symptoms and initial analysis.

### Hypothesis Format

For each hypothesis:
```
### H{N}: {Brief title} [{STATE}]
**Rationale:** Why this could be the cause
**Test approach:** How to verify/disprove
```

### User Selection

Present hypotheses and ask:
```
Which hypothesis to test first?
1. H1: {title}
2. H2: {title}
3. H3: {title}
4. Other - different theory
```

If "Other": Ask user to describe, then formulate as proper hypothesis.

## Test Strategies

| Hypothesis Type | Test Approach |
|-----------------|---------------|
| Service issue | Check process list, service status, ports |
| Config error | Read config files, check env vars |
| Code bug | Add logging, trace execution, run specific tests |
| Data issue | Query database, inspect state, check data integrity |
| Network issue | Check connectivity, ports, firewall, DNS |
| Permission issue | Check file/directory permissions, ownership |
| Dependency issue | Check versions, compatibility, lock files |

### Test Execution

1. Select appropriate commands/tools based on hypothesis type
2. Use Bash for commands, Read for config files, Grep for searching
3. Capture all output for documentation

## Record Outcome

After testing, update hypothesis with one of four outcomes:

| Outcome | When to Use | Document |
|---------|-------------|----------|
| REJECTED | Evidence disproves hypothesis | Test run, output, why it's ruled out |
| CONFIRMED | Evidence supports as root cause | Test run, output, how it explains symptoms |
| INCONCLUSIVE | Test didn't give clear answer | What was tried, why inconclusive |
| PARTIALLY CONFIRMED | Related but not root cause | Findings, suggest refined hypothesis |

### Update Debug Document

```markdown
### H{N}: {title} [{OUTCOME}]
**Rationale:** {original rationale}
**Test:** {what was executed}
**Result:** {observed output/behavior}
**Conclusion:** {interpretation of results}
```

### Investigation Log Entry

```markdown
### {timestamp} - Tested H{N}: {title}
- Ran: {commands/checks}
- Result: {findings}
- Conclusion: {outcome and next step}
```

## Loop Control

### Iteration Flow

After each hypothesis test:
1. If CONFIRMED -> Load resolution-recording.md
2. If user requests stop -> Save and pause session
3. Otherwise -> Form new hypotheses or test next

### Progress Summary (every 2-3 hypotheses)

```
## Debugging Progress
**Duration:** {time}
**Tested:** {N} hypotheses

### Results
- [REJECTED] H1: {title}
- [REJECTED] H2: {title}
- [TESTING] H3: {title}

### Patterns
{Any emerging insights}

Continue or different approach?
```

### Stuck Detection (4+ rejections)

If 4+ hypotheses rejected without progress:

```
## Debugging Checkpoint

Tested {N} hypotheses without finding root cause.

**Ruled out:**
{list of rejected hypotheses}

**Suggestions:**
1. Re-examine original symptoms
2. Reproduce with minimal code
3. Add comprehensive logging
4. Check if environmental (works elsewhere?)
5. Consider multiple factors combining

Options:
1. Add detailed logging and reproduce
2. Review symptoms again
3. Try completely different approach
4. Pause and return with fresh perspective
```

### Save Progress

At any point user can pause:
```
Session saved to: .tiki/debug/{session}.md
State: {N} hypotheses tested, last: H{N} ({state})
Resume: /tiki:debug --resume
```

## Transition Points

- **To resolution:** When hypothesis CONFIRMED, load `.tiki/prompts/debug/resolution-recording.md`
- **To exit:** When user requests pause/abandon, update session status and end
