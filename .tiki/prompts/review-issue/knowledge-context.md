# Knowledge Context for Review

**Load Condition:** Knowledge index exists (`.tiki/knowledge/index.json`).

## Purpose

Surface relevant institutional knowledge entries during issue review, adding them as PRIOR ART findings to inform planning decisions.

## Step 1: Load Knowledge Index

Read `.tiki/knowledge/index.json`. If empty or missing, skip silently.

## Step 2: Extract Keywords from Issue

Extract keywords for matching:

1. **Title**: Split into lowercase words, filter stopwords (the, a, an, is, to, for, and, or, with, etc.)
2. **Body**: Extract technology names, file paths, component names
3. **Labels**: Include label names as keywords

Convert all keywords to lowercase for case-insensitive matching.

## Step 3: Match Against Knowledge Index

For each non-archived entry in the index:

1. **Keyword match**: Count how many issue keywords match entry keywords
2. **File match**: Check if entry files overlap with issue-referenced files
3. **Calculate relevance**: Score = keyword matches + (file matches * 2)

Filter to entries with relevance score > 0. Sort by relevance descending. Limit to top 5 matches.

## Step 4: Format as PRIOR ART Findings

For each matched entry, create an info-level finding:

```json
{
  "severity": "info",
  "category": "PRIOR ART",
  "message": "Related past work: \"{title}\" ({id}) from Issue #{issueNumber}",
  "topic": "{id}"
}
```

## Output Format

Display matches to user:

```text
Knowledge context found:
- "{title}" ({id}) from Issue #{issueNumber} - {score} matches
```

**If no matches:** Skip silently (no message needed).

## Example Output

```text
### Info
- **[PRIOR ART]**: Related past work: "Auth Token Refresh Solution" (K001) from Issue #43
- **[PRIOR ART]**: Related past work: "Middleware Caching Pattern" (K003) from Issue #56
```

## YOLO Mode Integration

Include matched entries in the structured REVIEW_RESULT:

```json
{
  "info": [
    { "category": "PRIOR ART", "message": "Related past work: \"Auth Token Refresh Solution\" (K001) from Issue #43", "topic": "K001" }
  ]
}
```
