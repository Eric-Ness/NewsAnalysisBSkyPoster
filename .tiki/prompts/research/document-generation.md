# Research Document Generation

Conditional prompt loaded after all research agents complete. Use this to synthesize agent outputs into the final research document.

## Synthesis Process

### 1. Parse Agent Results

For each completed agent, extract:
- **Key Findings**: List of findings with confidence levels (High/Medium/Low)
- **Details**: Detailed content sections
- **Sources**: Table of URLs, titles, confidence, and notes

### 2. Combine by Dimension

Group findings into dimensions and sort by confidence (High first):
- Ecosystem Analysis
- Architecture Patterns
- Implementation Best Practices
- Common Pitfalls
- Recommendations

### 3. Deduplicate Sources

Merge sources across agents:
- Normalize URLs (remove trailing slashes, tracking params)
- Track which agents cited each source
- Use highest confidence when same source cited multiple times
- Sort by confidence, then citation count

### 4. Calculate Overall Confidence

Determine overall research confidence:
- **High**: 50%+ high-confidence findings, 40%+ high-quality sources, <20% low-confidence
- **Low**: 40%+ low-confidence findings OR <20% high-quality sources
- **Medium**: Everything else

### 5. Generate Executive Summary

Create 2-3 paragraphs covering:
1. Current ecosystem state (from ecosystem findings)
2. Key patterns and practices (from architecture + best practices)
3. Primary recommendation and critical pitfall

---

## Research Document Template

Write to `.tiki/research/{topic}/research.md`:

```markdown
---
topic: {topic}
researched_at: {ISO timestamp}
expires_at: {ISO timestamp + 7 days}
mode: {full|quick}
sources_count: {N}
agents_used: {N}
status: complete
overall_confidence: {high|medium|low}
---

# Research: {Topic Title}

> Researched on {date} | Mode: {full/quick} | Confidence: {high/medium/low}

## Executive Summary

{2-3 paragraphs synthesized from all agent findings}

## Ecosystem Analysis

### Available Libraries/Frameworks

| Library | Stars/Downloads | Last Update | Status | Notes |
|---------|-----------------|-------------|--------|-------|
| lib1 | 45k stars | 2026-01 | Active | Primary recommendation |

### Recommended Stack
{What most projects use, with rationale}

### Maintenance & Community
{Activity levels, community size, support options}

## Architecture Patterns

### Common Patterns

| Pattern | When to Use | Pros | Cons |
|---------|-------------|------|------|
| pattern1 | For X situations | Pro1, Pro2 | Con1, Con2 |

### Pattern Comparison
{Detailed comparison with selection criteria}

### Recommended Pattern
{Specific recommendation with rationale}

## Implementation Best Practices

### Project Structure
{Recommended directory layout}

### Testing Approach
{Testing patterns and frameworks}

### Error Handling
{Error handling patterns}

## Common Pitfalls

### Mistakes to Avoid
1. **Pitfall 1** [Confidence: High]
   - Why it happens: {explanation}
   - How to avoid: {solution}

### Performance Gotchas
{Performance issues with metrics/thresholds}

### Security Considerations
{Security concerns and mitigations}

## Recommendations

### Suggested Approach
{Primary recommendation with rationale}

### Alternative Approaches
{Other valid approaches with conditions}

### Next Steps
1. {Immediate action}
2. {Second priority}
3. {Third priority}

## Sources

| # | Source | Title | Confidence | Relevance |
|---|--------|-------|------------|-----------|
| 1 | [URL](url) | Title | High | Primary documentation |

## Research Log

- **Session:** {topic}
- **Started:** {timestamp}
- **Completed:** {timestamp}
- **Mode:** {full/quick}
- **Agents:** {N} completed, {N} failed
- **Findings:** {N} total ({N} high, {N} medium, {N} low confidence)
- **Sources:** {N} unique sources
```

---

## Section Guidelines

### Executive Summary
- Open with ecosystem state (1-2 sentences)
- Highlight primary recommendation (1-2 sentences)
- Note critical pitfall (1 sentence)
- Use clear, actionable language
- Stay within 2-3 paragraphs

### Ecosystem Analysis
- Include metrics: stars, downloads, last update date
- Note corporate backing/sponsorship
- Identify actively maintained vs legacy options
- Mention community resources (Discord, Stack Overflow)

### Architecture Patterns
- Use comparison tables for patterns
- Include specific guidance on when to use each
- Note scaling considerations
- Reference real-world examples if available

### Common Pitfalls
- Prioritize by impact and frequency
- Include both "why it happens" and "how to avoid"
- Separate performance, security, and general pitfalls
- Note version-specific issues

### Sources Table
- Number sources for reference
- Link URLs as markdown hyperlinks
- Include confidence rating per source
- Note what each source was used for (relevance)

### Confidence Notation
Use throughout: `[Confidence: High/Medium/Low]`
- **High**: Multiple authoritative sources agree
- **Medium**: Some sources agree or single authoritative source
- **Low**: Limited sources, conflicting info, or inference
