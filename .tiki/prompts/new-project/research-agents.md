# Project Research Agents

Configuration for spawning 4 parallel research agents to survey the domain ecosystem.

## Agent Overview

| Agent | Question | Output |
| ----- | -------- | ------ |
| Stack | What's the standard tech stack for this domain? | STACK.md |
| Features | What features do users expect? | FEATURES.md |
| Architecture | How are similar systems structured? | ARCHITECTURE.md |
| Pitfalls | What mistakes do teams commonly make? | PITFALLS.md |

## Spawn All 4 in Parallel

Use Task tool with `subagent_type: "general-purpose"` for each agent. Spawn all 4 simultaneously.

## Agent 1: Stack Research

```text
You are researching the technology stack for: [project domain]

## Your Focus
What's the standard 2026 stack for building [domain]?

## Research
1. Use WebSearch for "[domain] tech stack 2026", "[domain] recommended libraries"
2. Use WebFetch to read official docs for recommended technologies
3. Verify versions are current (not training data)

## Output
Write to: .tiki/research/project/STACK.md

Format:
# Technology Stack

## Recommended Stack

| Category | Technology | Version | Why |
| -------- | ---------- | ------- | --- |
| Language | [tech] | [ver] | [rationale] |
| Framework | [tech] | [ver] | [rationale] |
| Database | [tech] | [ver] | [rationale] |
| Testing | [tech] | [ver] | [rationale] |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
| -------- | ----------- | ----------- | ------- |

## Installation

[Package install commands]

## Sources

[URLs with confidence: HIGH/MEDIUM/LOW]
```

## Agent 2: Features Research

```text
You are researching features for: [project domain]

## Your Focus
What features do [domain] products have? What's table stakes vs differentiating?

## Research
1. Use WebSearch for "[domain] features", "[domain] MVP requirements"
2. Look at competitor products in this space
3. Identify what users expect vs what delights them

## Output
Write to: .tiki/research/project/FEATURES.md

Format:
# Feature Landscape

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity |
| ------- | ------------ | ---------- |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity |
| ------- | ----------------- | ---------- |

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What Instead |
| ------------ | --------- | ------------ |

## MVP Recommendation

For MVP, prioritize:
1. [Table stakes]
2. [One differentiator]

Defer to post-MVP:
- [Feature]: [reason]

## Sources

[URLs]
```

## Agent 3: Architecture Research

```text
You are researching architecture for: [project domain]

## Your Focus
How are [domain] systems typically structured? What are major components?

## Research
1. Use WebSearch for "[domain] architecture", "[domain] system design"
2. Look for component diagrams, data flow patterns
3. Identify common boundaries and interfaces

## Output
Write to: .tiki/research/project/ARCHITECTURE.md

Format:
# Architecture Patterns

## Recommended Architecture

[High-level description]

### Components

| Component | Responsibility | Communicates With |
| --------- | -------------- | ----------------- |

### Data Flow

[How data moves through the system]

## Patterns to Follow

### [Pattern Name]
**What:** [description]
**When:** [conditions]

## Anti-Patterns to Avoid

### [Anti-Pattern Name]
**What:** [description]
**Why Bad:** [consequences]
**Instead:** [alternative]

## Build Order

Suggested order based on dependencies:
1. [Component] — foundational, no dependencies
2. [Component] — depends on #1
3. [Component] — depends on #1, #2

## Sources

[URLs]
```

## Agent 4: Pitfalls Research

```text
You are researching pitfalls for: [project domain]

## Your Focus
What do [domain] projects commonly get wrong? Critical mistakes to avoid?

## Research
1. Use WebSearch for "[domain] common mistakes", "[domain] gotchas"
2. Look for post-mortems, lessons learned
3. Check Stack Overflow for frequent issues

## Output
Write to: .tiki/research/project/PITFALLS.md

Format:
# Domain Pitfalls

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### [Pitfall Name]
**What Goes Wrong:** [description]
**Why It Happens:** [root cause]
**Prevention:** [how to avoid]
**Warning Signs:** [early detection]

## Moderate Pitfalls

Mistakes that cause delays or tech debt.

### [Pitfall Name]
**What Goes Wrong:** [description]
**Prevention:** [how to avoid]

## Minor Pitfalls

Annoyances that are fixable.

### [Pitfall Name]
**What Goes Wrong:** [description]
**Prevention:** [how to avoid]

## Phase Warnings

| Phase Topic | Likely Pitfall | Mitigation |
| ----------- | -------------- | ---------- |

## Sources

[URLs]
```

## After All Agents Complete

Synthesize results into SUMMARY.md:

```text
# Research Summary: [Project Name]

**Domain:** [type]
**Researched:** [date]

## Key Findings

**Stack:** [one-liner from STACK.md]
**Table Stakes:** [top 3 from FEATURES.md]
**Architecture:** [pattern from ARCHITECTURE.md]
**Watch Out For:** [top pitfall from PITFALLS.md]

## Implications for Requirements

Based on research:
- Must have: [features]
- Consider: [features]
- Avoid: [anti-features]

## Files

| File | Purpose |
| ---- | ------- |
| STACK.md | Technology recommendations |
| FEATURES.md | Feature landscape |
| ARCHITECTURE.md | System structure |
| PITFALLS.md | Common mistakes |
```

## Confidence Levels

Mark findings with confidence:

- **HIGH** — Official docs, Context7, multiple sources agree
- **MEDIUM** — Reputable blog + one other source
- **LOW** — Single source, unverified, or training data only

Flag LOW confidence findings for validation.
