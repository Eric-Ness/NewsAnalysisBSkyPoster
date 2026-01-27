# Alternative Analysis

Explore alternative approaches when issue involves complex decisions or when `--alternatives` flag is used.

## Analysis Areas

### Existing Patterns
Search the codebase for:
- Similar functionality already implemented
- Patterns that solve related problems
- Reusable components or utilities
- Prior art that can be referenced

Use Glob/Grep to find related files and Read to understand existing implementations.

### Library Alternatives
Consider:
- Standard library solutions vs external dependencies
- Well-maintained alternatives with better fit
- Lighter-weight options for simple needs
- More feature-rich options if complexity warranted

### Architectural Approaches
Evaluate different approaches:
- Synchronous vs asynchronous processing
- Client-side vs server-side logic
- Monolithic vs modular structure
- Push vs pull data patterns

### Trade-off Analysis

For each alternative, evaluate:

| Factor | Weight | Consideration |
|--------|--------|---------------|
| Complexity | High | Implementation and maintenance burden |
| Performance | Medium | Runtime efficiency |
| Flexibility | Medium | Future extensibility |
| Consistency | High | Alignment with existing patterns |
| Time | High | Implementation timeline impact |

## Prior Art Detection

Search for similar patterns:
```
1. Glob for files with similar naming (e.g., *auth*, *user*)
2. Grep for similar function/class patterns
3. Read key files to understand approach
4. Note reusable patterns and utilities
```

## Output Format

### Alternative Approaches Section

```text
### Alternative Approaches
1. **[Approach Name]**: Brief description
   - Pros: List advantages
   - Cons: List disadvantages
   - Recommendation: When to choose this

2. **[Prior Art]**: Similar pattern in `<file-path>`
   - Can be reused/extended for this use case
```

### Info-Level Findings

```json
{
  "severity": "info",
  "category": "alternative",
  "message": "Alternative approach available: <description>",
  "reference": "optional file or resource reference"
}
```

```json
{
  "severity": "info",
  "category": "prior_art",
  "message": "Similar pattern exists in <file>",
  "reference": "path/to/file.ts"
}
```

## When to Recommend Alternatives

- Current approach significantly more complex than alternatives
- Existing pattern in codebase solves same problem
- Well-known library provides better solution
- Architectural mismatch with existing codebase

**Note:** Alternatives are informational. Do not block on alternatives unless current approach is fundamentally flawed.
