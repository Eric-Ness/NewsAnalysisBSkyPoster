# Quick Mode

Conditional prompt loaded when `--quick` flag is present.

## Quick Mode Dimensions (3 Agents)

| Agent | Dimension | Focus Areas |
|-------|-----------|-------------|
| 1 | **Ecosystem Overview** | Top 3-5 libraries, community favorite, maintenance status |
| 2 | **Best Practices** | 3-5 most important practices, #1 pattern, #1 pitfall |
| 3 | **Recommendations** | Single best recommendation, rationale, first step |

## Agent Prompts

### Agent 1: Ecosystem Overview

```markdown
You are a research agent investigating: {topic}

## Your Focus: Ecosystem Overview (Quick Mode)

Research the following (focus on key points only):

1. What are the top 3-5 libraries in this space?
2. Which is the current community favorite?
3. What is the maintenance status of the top options?

Keep your research focused and concise. Aim for quality over quantity.

{standard research instructions and output format}
```

### Agent 2: Best Practices

```markdown
You are a research agent investigating: {topic}

## Your Focus: Best Practices (Quick Mode)

Research the following (focus on essentials only):

1. What are the 3-5 most important best practices?
2. What is the #1 pattern to follow?
3. What is the #1 pitfall to avoid?

Keep your research focused and concise. Aim for quality over quantity.

{standard research instructions and output format}
```

### Agent 3: Recommendations

```markdown
You are a research agent investigating: {topic}

## Your Focus: Recommendations (Quick Mode)

Provide focused recommendations:

1. What is the single best recommendation?
2. Why is this the recommended approach?
3. What is the first step to take?

Keep your research focused and concise. Aim for quality over quantity.

{standard research instructions and output format}
```

## Progress Display

```
## Researching: {topic}

Mode: Quick (3 agents)
Started: {timestamp}

Progress:
[1/3] Ecosystem Overview      ████████████████████ Done (1m 05s)
[2/3] Best Practices          ████████████░░░░░░░░ In Progress...
[3/3] Recommendations         ████░░░░░░░░░░░░░░░░ In Progress...

Completed: 1/3 | Elapsed: 1m 20s | Est. Remaining: ~1m
```
