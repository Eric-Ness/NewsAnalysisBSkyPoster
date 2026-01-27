---
type: prompt
name: tiki:research
description: Research unfamiliar domains before planning. Use when you need to understand a technology, library, or pattern before implementing.
allowed-tools: Read, Write, Bash, Glob, Grep, Task, WebSearch, WebFetch, AskUserQuestion
argument-hint: <topic|#issue|query> [--refresh] [--quick]
---

# Research

Research unfamiliar domains before planning to ensure implementations follow current best practices.

## Usage

```
/tiki:research react-query                    # Research a topic
/tiki:research #42                            # Research topics from issue
/tiki:research "auth patterns for Next.js"   # Free-form query
/tiki:research react-query --refresh         # Force refresh existing
/tiki:research react-query --quick           # Quick mode (3 agents)
```

## Instructions

### Step 1: Parse Arguments

Determine research target and flags from input:

| Input Pattern | Type | Action |
|---------------|------|--------|
| `#N` or number | Issue | Fetch issue, extract topics from title/body/labels |
| `"quoted text"` | Query | Use as query, generate kebab-case folder name |
| `unquoted-text` | Topic | Use as topic, convert to kebab-case folder |
| (no args) | Error | Show usage |

**Flags:** `--refresh` (force new research), `--quick` (3 agents instead of 5)

**Folder naming:** Convert to kebab-case (e.g., `ReactQuery` -> `react-query`)

### Step 2: Check Cache

Check for existing research at `.tiki/research/{topic}/research.md`

**If exists and no --refresh:**
```
## Existing Research Found

Research for "{topic}" exists.
Researched: {age} ago | Mode: {mode} | Sources: {N}

Options: 1) View  2) Refresh  3) Supplement  4) Cancel
```

**If --refresh flag:** Read `.tiki/prompts/research/refresh-mode.md` and follow workflow.

**If no cache:** Create directory and continue.

### Step 3: Initialize Session

```
## Research Session: {topic}
Mode: {full/quick} | Cache: {new/refresh}
```

Create shell document at `.tiki/research/{topic}/research.md` with frontmatter:
```yaml
topic: {topic}
researched_at: {ISO}
expires_at: {ISO + 7 days}
mode: {full|quick}
status: in_progress
```

### Step 4: Spawn Research Agents

**If --quick flag:** Read `.tiki/prompts/research/quick-mode.md` for 3-agent configuration.

**Full mode (default):** Spawn 5 parallel agents via Task tool:

| Agent | Dimension | Focus |
|-------|-----------|-------|
| 1 | Ecosystem | Libraries, popularity, maintenance, community |
| 2 | Architecture | Patterns, pros/cons, scaling, real-world examples |
| 3 | Best Practices | Project structure, testing, error handling, workflow |
| 4 | Pitfalls | Common mistakes, performance, security, debugging |
| 5 | Recommendations | Suggested approach, rationale, alternatives, next steps |

**Agent prompt template:**
```
You are a research agent investigating: {topic}

## Your Focus: {dimension}
{dimension_questions}

## Instructions
1. Use WebSearch for current information (2026)
2. Use WebFetch to read relevant pages
3. Note source confidence: High (official docs), Medium (reputable blogs), Low (random/outdated)

## Output Format
## {Dimension}
### Key Findings
- Finding [Confidence: High/Medium/Low]
### Details
{content}
### Sources
| URL | Title | Confidence | Notes |
```

### Step 5: Collect Results

Wait for all agents, display progress:
```
[1/5] Ecosystem Analysis     ✓ Done
[2/5] Architecture Patterns  ... Running
```

Handle failures with retry/skip options. Store raw outputs in `.tiki/research/{topic}/agents/`.

### Step 6: Synthesize & Generate Document

Read `.tiki/prompts/research/document-generation.md` and follow to:
1. Parse and combine agent results by dimension
2. Deduplicate sources
3. Calculate overall confidence
4. Generate executive summary
5. Write final `.tiki/research/{topic}/research.md`

### Step 7: Update Index

Read `.tiki/prompts/research/index-management.md` and follow to:
1. Generate aliases for topic
2. Update `.tiki/research/index.json`

### Step 8: Display Summary

```
## Research Complete: {topic}

Mode: {full/quick} | Sources: {N} | Confidence: {high/medium/low}

### Key Recommendations
1. {primary recommendation}
2. {secondary recommendation}
3. {key pitfall to avoid}

### Output
Research: .tiki/research/{topic}/research.md
Index: .tiki/research/index.json ({N} aliases)

Commands:
  View: cat .tiki/research/{topic}/research.md
  Plan: /tiki:plan-issue {N}
```

## Notes

- Research cached 7 days; use `--refresh` for new research
- Full mode: 5 agents, comprehensive. Quick mode: 3 agents, faster
- Agent failures handled with retry/skip options
- Sources include confidence levels for reliability assessment
