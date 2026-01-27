# Index Management

Conditional prompt loaded after research document is written. Updates `.tiki/research/index.json` for fast topic lookups.

## Index Schema

```json
{
  "lastUpdated": "ISO timestamp",
  "topics": {
    "topic-name": {
      "researched_at": "ISO timestamp",
      "expires_at": "ISO timestamp",
      "confidence": "high|medium|low",
      "aliases": ["alias1", "alias2"]
    }
  }
}
```

## Alias Generation

Generate aliases from multiple sources:

1. **Common variations** of the topic name:
   - PascalCase: `react-query` -> `ReactQuery`
   - With spaces: `react-query` -> `React Query`
   - Lowercase joined: `react-query` -> `reactquery`

2. **From ecosystem findings**:
   - npm package names (e.g., `@tanstack/react-query`)
   - Quoted library names in findings

3. **From source titles**:
   - Extract capitalized versions that match the topic

## Update Workflow

1. **Read existing index** (or create empty structure if missing):
   ```json
   { "lastUpdated": null, "topics": {} }
   ```

2. **Build topic entry**:
   - `researched_at`: From research document metadata
   - `expires_at`: From research document metadata
   - `confidence`: Overall confidence from synthesis
   - `aliases`: Generated aliases array

3. **Merge and write**:
   - Update `lastUpdated` timestamp
   - Add/replace topic entry in `topics` object
   - Write to `.tiki/research/index.json`

4. **Confirm update**:
   ```
   Index updated: .tiki/research/index.json
   Topics tracked: {N}
   Aliases for "{topic}": {alias1}, {alias2}, ...
   ```
