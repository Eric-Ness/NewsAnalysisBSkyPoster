# Knowledge Search Workflow

## Step 1: Parse Query

Extract search terms from the query:
- Split on spaces
- Convert to lowercase
- Remove common stop words

## Step 2: Search Index

Read `.tiki/knowledge/index.json` and search:

1. **Keyword matching:** Check if any search term matches entry keywords (case-insensitive)
2. **Title matching:** Check if any search term appears in entry title
3. **Calculate relevance:** Count total keyword matches per entry

```javascript
// Pseudo-code for relevance scoring
for each entry in index.entries:
  score = 0
  for each searchTerm in queryTerms:
    for each keyword in entry.keywords:
      if keyword.toLowerCase().includes(searchTerm):
        score += 2  // Keyword match worth 2
    if entry.title.toLowerCase().includes(searchTerm):
      score += 1  // Title match worth 1
  if score > 0:
    matches.push({ id, entry, score })
```

## Step 3: Sort and Filter

1. Filter out archived entries (unless `--all` flag)
2. Sort by relevance score (highest first)
3. Limit to top 20 results

## Step 4: Display Results

**If matches found:**

```
## Search Results: "{query}"

Found {N} entries matching your query.

| ID   | Title                          | Relevance | Confidence | Keywords Matched        |
|------|--------------------------------|-----------|------------|-------------------------|
| K003 | Rate limiting with Redis       | 5         | high       | redis, rate-limit, api  |
| K001 | API error handling patterns    | 3         | medium     | api, error              |

View entry: /tiki:knowledge show K###
```

**If no matches:**

```
## Search Results: "{query}"

No entries found matching "{query}".

Suggestions:
- Try different keywords
- Check spelling
- Use broader terms
- List all: /tiki:knowledge list
```

## Step 5: Quick View Option

If only 1-3 results, offer to show content inline:

```
Only {N} result(s) found. Show content inline? [Y/n]
```

If yes, display full entry content for each match.
