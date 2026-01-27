---
type: prompt
name: tiki:new-project
description: Initialize a new project through deep questioning, optional research, requirements scoping, and GitHub issue generation.
allowed-tools: Bash, Read, Write, Glob, Grep, Task, WebSearch, WebFetch, AskUserQuestion
argument-hint: [--skip-research] [--skip-issues]
---

# New Project

Initialize a project through: questioning → research (optional) → requirements → GitHub issues.

## Usage

```text
/tiki:new-project
/tiki:new-project --skip-research    # Skip domain research
/tiki:new-project --skip-issues      # Skip GitHub issue creation
```

## Instructions

### Phase 1: Setup

**Run these checks first:**

```bash
# Check for existing PROJECT.md
[ -f PROJECT.md ] && echo "PROJECT_EXISTS" || echo "NO_PROJECT"

# Check for existing code (brownfield detection)
find . -maxdepth 2 -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" 2>/dev/null | grep -v node_modules | head -5
[ -f package.json ] || [ -f requirements.txt ] || [ -f go.mod ] && echo "HAS_MANIFEST"

# Check for .tiki/STACK.md (already mapped)
[ -f .tiki/STACK.md ] && echo "CODEBASE_MAPPED"
```

**If PROJECT_EXISTS:** Ask user - View existing, Overwrite (backup first), or Cancel.

**If code detected AND not mapped:** Offer `/tiki:map-codebase` first. If declined, continue.

**Ensure git repo:**

```bash
[ -d .git ] || git init
```

### Phase 2: Deep Questioning

Read `.tiki/prompts/new-project/deep-questioning.md` for techniques.

**Start open:** "What do you want to build?"

Follow threads from their response. Challenge vagueness, make abstract concrete, surface assumptions. Cover:

- Vision (the big picture)
- Core problem being solved
- Target users
- Key constraints
- What's explicitly NOT in scope

**Decision gate:** When you could write a clear PROJECT.md, use AskUserQuestion:

- "Ready to create PROJECT.md?" → Create / Keep exploring

### Phase 3: Generate PROJECT.md

Read `.tiki/prompts/new-project/project-templates.md` for template.

Write `PROJECT.md` with gathered context. Include Requirements section as hypotheses:

```markdown
## Requirements

### Validated
(None yet — ship to validate)

### Active
- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Out of Scope
- [Exclusion 1] — [why]
```

Store raw responses in `.tiki/project-config.json`.

Commit:

```bash
mkdir -p .tiki
git add PROJECT.md .tiki/project-config.json
git commit -m "docs: initialize project - [project name]"
```

### Phase 4: Research Decision

**Skip if `--skip-research` flag.**

Use AskUserQuestion:

- header: "Research"
- question: "Research the domain ecosystem before defining requirements?"
- options:
  - "Research first (Recommended)" — Discover standard stacks, expected features, architecture patterns
  - "Skip research" — I know this domain well

**If research selected:**

Read `.tiki/prompts/new-project/research-agents.md` for agent configuration.

Create directory and spawn 4 parallel agents via Task tool:

```bash
mkdir -p .tiki/research/project
```

| Agent | Focus | Output |
| ----- | ----- | ------ |
| Stack | Technologies, libraries, versions | STACK.md |
| Features | Table stakes, differentiators, anti-features | FEATURES.md |
| Architecture | Patterns, components, data flow | ARCHITECTURE.md |
| Pitfalls | Common mistakes, prevention strategies | PITFALLS.md |

After agents complete, synthesize into SUMMARY.md.

Commit research:

```bash
git add .tiki/research/project/
git commit -m "docs: add project research"
```

### Phase 5: Requirements Scoping

Read `.tiki/prompts/new-project/feature-scoping.md` for workflow.

**If research exists:** Present features by category from FEATURES.md.

**If no research:** Gather requirements conversationally.

For each category, use AskUserQuestion with multiSelect:

- Which features are in v1?
- Selected → v1 requirements
- Unselected table stakes → v2
- Unselected differentiators → out of scope

Generate `.tiki/requirements.json` and `.tiki/REQUIREMENTS.md` with REQ-IDs (e.g., AUTH-01, CORE-02).

Commit:

```bash
git add .tiki/requirements.json .tiki/REQUIREMENTS.md
git commit -m "docs: define v1 requirements - [count] requirements"
```

### Phase 6: Issue Generation

**Skip if `--skip-issues` flag.**

Read `.tiki/prompts/new-project/issue-generation.md` for workflow.

Use AskUserQuestion:

- header: "GitHub Issues"
- question: "Create GitHub issues from requirements?"
- options:
  - "Create issues (Recommended)" — Generate issues ready for /tiki:yolo
  - "Skip for now" — I'll create issues manually later

**If create issues:**

For each requirement (or logical grouping):

1. Create issue with title, body, labels
2. Add dependency references in body
3. Optionally create v1 milestone and assign

Display created issues summary.

### Phase 7: Completion

Display summary:

```text
## Project Initialized

**[Project Name]**

| Artifact | Location |
|----------|----------|
| Project | PROJECT.md |
| Config | .tiki/project-config.json |
| Research | .tiki/research/project/ (if created) |
| Requirements | .tiki/REQUIREMENTS.md |
| Issues | [count] created (if created) |

## Next Steps

- `/tiki:pick-issue` — See which issue to start with
- `/tiki:yolo [number]` — Execute an issue end-to-end
- `/tiki:plan-issue [number]` — Plan an issue manually
```

## Notes

- Deep questioning follows threads, not rigid Q&A
- Research is optional but recommended for unfamiliar domains
- Requirements use REQ-IDs for traceability
- GitHub issues are the "roadmap" in Tiki's issue-centric model
- Conditional prompts in `.tiki/prompts/new-project/`:
  - `deep-questioning.md` - Questioning techniques
  - `project-templates.md` - PROJECT.md and config templates
  - `tech-stack-analysis.md` - Brownfield stack detection
  - `research-agents.md` - Project research agent specs
  - `feature-scoping.md` - Category-based feature selection
  - `issue-generation.md` - Requirements to GitHub issues
