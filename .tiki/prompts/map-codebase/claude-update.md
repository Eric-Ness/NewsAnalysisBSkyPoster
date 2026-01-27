# CLAUDE.md Update

Append discovered patterns to CLAUDE.md when --update-claude flag is present.

## Instructions

After analyzing the codebase and generating documentation, append the following section to CLAUDE.md:

## Content to Append

```markdown
## Discovered Patterns

> Added by /tiki:map-codebase on {date}

### Code Organization
- Services are in `{services_dir}`
- API routes are in `{api_dir}`
- Shared types are in `{types_dir}`
- Components are in `{components_dir}`

### Naming Conventions
- Files: {file_convention} ({example})
- Components: {component_convention} ({example})
- Functions: {function_convention} ({example})
- Variables: {variable_convention} ({example})

### Testing
- Tests location: {test_location} ({pattern})
- Test framework: {framework}
- Mocking approach: {mocking}
- E2E tests: {e2e_location}
```

## Implementation

1. Read existing CLAUDE.md
2. Check if "## Discovered Patterns" section already exists
3. If exists: Replace existing section with updated content
4. If not exists: Append to end of file
5. Write updated CLAUDE.md

## Notes

- Replace all {placeholders} with actual discovered values from analysis
- Only include sections where patterns were detected
- Keep the format consistent with existing CLAUDE.md style
- Include the date for tracking when patterns were discovered
