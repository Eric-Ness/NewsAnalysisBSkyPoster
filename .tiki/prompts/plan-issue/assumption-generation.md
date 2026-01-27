# Assumption Generation

**Load Condition:** No assumptions imported from prior review (no `<!-- REVIEW_RESULT ... REVIEW_RESULT -->` marker in issue comments).

## Purpose

Generate assumptions during planning when no prior `/tiki:review-issue` was performed.

## Step 1: Check for Existing Review Assumptions

Search issue comments for the review result marker:

```bash
gh issue view {number} --json comments --jq '.comments[].body'
```

Look for `<!-- REVIEW_RESULT ... REVIEW_RESULT -->` containing JSON with assumptions array.

If found:
- Parse the JSON between markers
- Extract `assumptions` array
- Set `source: 'review'` and `imported: true`

## Step 2: Generate Assumptions Inline

If no prior review found, generate assumptions by analyzing:

### Technical Assumptions (High Confidence)
Inferred from codebase structure:
- **Database**: Check for migrations, schema files, ORM configs
- **Test framework**: Check for test files, testing dependencies
- **Language/Framework**: Check for config files (package.json, Cargo.toml, etc.)

### Scope Assumptions (Medium Confidence)
Inferred from issue content:
- Features explicitly mentioned vs not mentioned
- Edge cases that need clarification
- Performance requirements (if not specified)

### Integration Assumptions (Low Confidence)
Inferred from project structure:
- Dependencies on existing modules
- Expected interfaces with other components
- API patterns (REST, GraphQL, etc.)

### Assumption Format

```json
{
  "id": "A1",
  "confidence": "high",
  "description": "Database uses PostgreSQL",
  "source": "existing migrations in /migrations/",
  "affectsPhases": []
}
```

## Step 3: Store Assumptions

```json
{
  "assumptions": [...],
  "source": "review" | "generated",
  "imported": true | false
}
```

The `affectsPhases` array is populated later in Step 4.5 (Map Assumptions to Phases).

## Step 4: Display Assumptions Discovery

**If imported from review:**

```text
## Assumptions Imported from Review

Found {N} assumptions from prior issue review:

**High Confidence:**
- {A1}: {description} (source: {source})

**Medium Confidence:**
- {A2}: {description} (source: {source})

**Low Confidence:**
- {A3}: {description} (source: {source})

These assumptions will be mapped to phases during planning.
```

**If generated inline:**

```text
## Assumptions Generated

Generated {N} assumptions based on issue and codebase analysis:

**High Confidence:**
- {A1}: {description} (source: {source})

**Medium Confidence:**
- {A2}: {description} (source: {source})

**Low Confidence:**
- {A3}: {description} (source: {source})

These assumptions will be mapped to phases during planning.
```

**If no assumptions:** Skip silently and continue.

## Display in Final Plan

Include Assumptions section in Step 6 display (after Research Context, before Success Criteria):

```markdown
### Assumptions

*{Imported from prior issue review | Generated during planning}*

**High Confidence:**
- {A1}: {description} (source: {source}) - affects Phase {phases}

**Medium Confidence:**
- {A2}: {description} (source: {source}) - affects Phase {phases}

**Low Confidence:**
- {A3}: {description} (source: {source}) - {affects Phase X | global assumption}

---
```

Assumptions with empty `affectsPhases` are labeled "global assumption".
