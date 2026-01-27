# ADR Auto-Generation

During execution, when Claude makes significant decisions, it should auto-generate ADRs.

## Trigger Conditions

Auto-generate an ADR when:
- Choosing between libraries/frameworks
- Selecting architectural patterns
- Making security-related choices
- Deciding on data modeling approaches
- Picking testing strategies
- Establishing API design conventions
- Choosing infrastructure/deployment approaches

## Auto-Generation Workflow

1. **Recognize decision point** - Identify when a significant technical choice is being made
2. **Capture context** - Note the alternatives considered and reasoning
3. **Generate ADR** - Create the ADR file automatically
4. **Continue execution** - Resume work after recording

## Example Flow

```
I chose to implement the repository pattern for data access.

Auto-generating ADR...

Created: .tiki/adr/004-use-repository-pattern.md

This decision has been recorded for future reference.
Continuing with implementation...
```

## Auto-Generated ADR Content

When auto-generating, include:
- The decision context from current work
- Alternatives that were considered (even briefly)
- Why this option was chosen
- Link to the current issue/phase if applicable

## Notes

- Keep auto-generated ADRs concise
- They can be expanded later via `/tiki:adr update`
- Record the decision even if brief - future developers benefit from knowing "why"
- Include enough context that the reasoning is clear
