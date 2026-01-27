# Changelog Generation

Generate a changelog for the shipped release.

## When to Load

Load this prompt when `--changelog` flag is provided.

## Execution

Generate changelog from completed issues:

```bash
# Get issue details for changelog
for issue in release.issues:
  gh issue view ${issue.number} --json title,labels,body --jq '{title,labels,body}'
done
```

## Changelog Format

```markdown
# Changelog - {version}

**Released:** {shippedAt}
**Issues:** {issueCount}

## Changes

{For each issue, grouped by label/type:}

### Features
- {issue.title} (#{issue.number})

### Bug Fixes
- {issue.title} (#{issue.number})

### Documentation
- {issue.title} (#{issue.number})

## Contributors

{List unique authors from issue assignments}
```

## Output Options

1. **Display only** - Show changelog in terminal
2. **Write to file** - Save to `CHANGELOG.md` or append to existing
3. **Copy to clipboard** - For pasting elsewhere

## Notes

- Group issues by their GitHub labels
- Use conventional commit categories: Features, Bug Fixes, Documentation, Other
- Include issue numbers as references
- If no labels, place under "Other"
