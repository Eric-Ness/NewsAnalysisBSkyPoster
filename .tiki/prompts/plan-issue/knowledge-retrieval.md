# Knowledge Retrieval

**Load Condition:** Knowledge index exists (`.tiki/knowledge/index.json`).

## Purpose

Surface relevant institutional knowledge entries when planning new issues, helping inform decisions based on past learnings.

## Step 1: Load Knowledge Index

Read `.tiki/knowledge/index.json`. If it doesn't exist, skip knowledge retrieval silently.

## Step 2: Extract Keywords from Issue

Extract keywords from the issue for matching:

1. **Title**: Split into lowercase words, filter common words (the, a, an, is, to, for, etc.)
2. **Body**: Extract technology names, file paths, and component names
3. **Labels**: Include label names as keywords

Convert all keywords to lowercase for case-insensitive matching.

## Step 3: Match Against Knowledge Index

For each non-archived entry in the index:

1. **Keyword match**: Count how many issue keywords match entry keywords
2. **File match**: Check if entry files overlap with issue-referenced files
3. **Calculate relevance**: Score = keyword matches + (file matches * 2)

Filter to entries with relevance score > 0. Sort by relevance descending.

## Step 4: Display Matches

**If matches found:**

```text
## Knowledge Context Detected

Found {N} related knowledge entries:

| Entry | Title | Source | Relevance |
|-------|-------|--------|-----------|
| {id} | {title} | Issue #{issueNumber} | {score} matches |

Knowledge insights will be incorporated into phase planning.
```

**If no matches:**

Skip silently (no message needed).

## Step 5: Store Knowledge Context

Store matched entries for use in phase generation and plan file:

```json
{
  "matched": ["K001", "K003"],
  "keywords": ["authentication", "middleware", "jwt"],
  "displayed": true
}
```

## Integration with Phase Planning

When generating phases, reference relevant knowledge:

1. **Include in phase content**: Mention relevant past learnings
2. **Add `knowledgeReferences` field**: List entry IDs that inform the phase
3. **Prioritize high-confidence entries**: Weight higher confidence entries more

Example phase content with knowledge:

```markdown
**Knowledge Reference:** K001 - JWT token validation patterns

**From past work:**
- Use middleware pattern from src/middleware/auth.ts
- Remember to handle token expiration edge case
```

## Display in Final Plan

Include Knowledge Context section in Step 6 display:

```markdown
### Knowledge Context (if applicable)

Relevant past work:
- **{title}** ({id}) - from Issue #{issueNumber}
- **{title}** ({id}) - from Issue #{issueNumber}
```
