# Research Integration

**Load Condition:** Research index exists (`.tiki/research/index.json`) AND `--no-research` flag is NOT provided.

## Purpose

Incorporate relevant research into the planning process by matching issue keywords against existing research documents.

## Step 1: Check Research Index

Read `.tiki/research/index.json`. If it doesn't exist, skip research integration silently.

## Step 2: Extract Keywords from Issue

Extract technology names, patterns, and keywords from the issue:

1. **Issue content**: Scan title and body for technology names (react, vue, prisma, jest, etc.)
2. **Labels**: Include label names as keywords
3. **Patterns**: Look for kebab-case terms (e.g., `react-query`, `styled-components`)

Convert all keywords to lowercase kebab-case for matching.

## Step 3: Match Against Research Index

For each topic in the index, check for matches:

1. **Direct match**: Keyword matches topic folder name exactly
2. **Alias match**: Keyword matches any alias in `topic.aliases[]`

## Step 4: Check Freshness

For each matched research, calculate age from `researched_at`:

| Age | Status |
|-----|--------|
| < 7 days | Fresh |
| 7-30 days | Current |
| > 30 days | STALE - suggest refresh |

## Step 5: Extract Key Sections

For each matched research, read `.tiki/research/{topic}/research.md` and extract:

- **Executive Summary**: Overview of findings
- **Recommendations/Suggested Approach**: Key patterns to follow
- **Common Pitfalls** (first 3 items): Mistakes to avoid

## Step 6: Store Research Context

Store for use in phase generation:

```json
{
  "matches": [
    {
      "topic": "react-query",
      "confidence": "high",
      "matchType": "direct",
      "freshness": { "ageDays": 3, "isStale": false },
      "sections": { "executiveSummary": "...", "suggestedApproach": "...", "mistakesToAvoid": "..." },
      "path": ".tiki/research/react-query/research.md"
    }
  ],
  "keywords": ["react", "data-fetching"],
  "hasResearch": true
}
```

## Step 7: Display Research Discovery

**If matches found:**

```text
## Research Context Detected

Found {N} relevant research document(s) based on issue keywords:

Keywords extracted: {keyword1}, {keyword2}, {keyword3}...

Matched research:
- **{topic1}** ({confidence} confidence) - researched {ageText}
- **{topic2}** ({confidence} confidence) - researched {ageText} [STALE - consider refreshing]

Research insights will be incorporated into phase planning.
```

**If no matches:**

```text
No relevant research found for this issue.
Consider running /tiki:research before planning if this involves unfamiliar technology.
```

## Integration with Phase Planning

When generating phases, incorporate research:

1. **Reference research in phase content**: Include relevant recommendations
2. **Add `researchReferences` field**: List topic names that inform the phase
3. **Note stale research**: Add warning if research > 30 days old
4. **Suggest refresh**: For stale research, recommend `/tiki:research {topic} --refresh`

Example phase content with research:

```markdown
**Research Reference:** react-query (researched 3 days ago)

**From research - Key patterns:**
- Use query keys as arrays for proper cache invalidation
- Implement stale-while-revalidate for better UX

**From research - Avoid:**
- Mixing server state with local UI state
```

## Display in Final Plan

Include Research Context section in Step 6 display:

```markdown
### Research Context

Relevant research found:
- **{topic}** (researched {age}) - [View full research](.tiki/research/{topic}/research.md)

#### Key Recommendations
- {executiveSummary highlights}
- {suggestedApproach}
- Avoid: {mistakesToAvoid}
```

For stale research, add warning:
```markdown
**Warning:** This research is over 30 days old. Consider refreshing:
`/tiki:research {topic} --refresh`
```
