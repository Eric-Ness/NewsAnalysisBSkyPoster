# Context Budget Estimation

Estimate context window usage for the current/next phase execution.

## Data Sources

1. **Active plan file** (`.tiki/plans/issue-N.json`):
   - Phase content length (characters)
   - Files per phase (count)
   - Verification items

2. **Current state** (`.tiki/state/current.json`):
   - Completed phase summaries

3. **CLAUDE.md** (if exists):
   - Project context size

## Token Estimation Formula

Use ~4 characters per token as a rough heuristic:

```javascript
phaseContentTokens = phase.content.length / 4
filesEstimate = phase.files.length * 500  // ~500 tokens per file read
verificationTokens = phase.verification.join('\n').length / 4
claudeMdTokens = claudeMdContent.length / 4
previousSummariesTokens = completedPhases.map(p => p.summary.length).reduce((a,b) => a+b, 0) / 4
totalEstimate = phaseContentTokens + filesEstimate + verificationTokens + claudeMdTokens + previousSummariesTokens
```

## Usage Level Thresholds

Categorize context usage:
- **Low** (green): < 30K tokens - `[####------]`
- **Medium** (yellow): 30K-60K tokens - `[######----]`
- **High** (orange): 60K-80K tokens - `[########--]`
- **Critical** (red): > 80K tokens - `[##########]`

## Warning for Large Phases

If total estimate > 40K tokens, flag a warning:
```
Warning: Large phase detected (~45K tokens). Sub-agent may need to break work into smaller steps.
```

## Summary Growth Tracking

Track summary growth across completed phases:
- Calculate average summary size per phase
- If total summaries exceed 2K tokens, note the growth:
```
Summary growth: 2,400 tokens across 4 phases (avg 600/phase)
Consider: Summaries may be too detailed for long-running issues
```

## Display Format

```text
### Context Budget (Next Phase)

| Component | Est. Tokens |
|-----------|-------------|
| Phase content | ~1,250 |
| Files (~3) | ~1,500 |
| CLAUDE.md | ~800 |
| Previous summaries | ~400 |
| Verification | ~100 |
| **Total** | **~4,050** |

Usage: [####------] Low (~4K of 100K)
```
