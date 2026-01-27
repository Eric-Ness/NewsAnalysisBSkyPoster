---
type: prompt
name: tiki:map-codebase
description: Analyze codebase and generate .tiki/STACK.md and .tiki/CONCERNS.md. Use when starting with a new codebase or refreshing documentation.
allowed-tools: Read, Write, Bash, Glob, Grep, Task
argument-hint: [--stack-only] [--concerns-only] [--update-claude] [--conventions] [--testing] [--integrations] [--all-docs]
---

# Map Codebase

Analyze an existing codebase to generate documentation about the tech stack and known concerns.

## Usage

```
/tiki:map-codebase                    # Generate STACK.md and CONCERNS.md
/tiki:map-codebase --stack-only       # Generate only STACK.md
/tiki:map-codebase --concerns-only    # Generate only CONCERNS.md
/tiki:map-codebase --conventions      # Also generate CONVENTIONS.md
/tiki:map-codebase --testing          # Also generate TESTING.md
/tiki:map-codebase --integrations     # Also generate INTEGRATIONS.md
/tiki:map-codebase --all-docs         # Generate all optional docs
/tiki:map-codebase --update-claude    # Also update CLAUDE.md
```

## Instructions

### Step 0: Parse Flags

Parse arguments to determine scope:

- `--stack-only` / `--concerns-only`: Generate only specified doc
- `--conventions` / `--testing` / `--integrations`: Include that optional doc
- `--all-docs`: Include all optional docs (CONVENTIONS, TESTING, INTEGRATIONS)
- `--update-claude`: Update CLAUDE.md with discovered patterns

If no flags provided (default), generate STACK.md and CONCERNS.md only.

### Step 1: Analyze Project Structure

Use Glob and directory listing to understand layout:

- Package files: `**/package.json`, `**/requirements.txt`, `**/Cargo.toml`, `**/go.mod`
- Config files: `**/tsconfig.json`, `**/webpack.config.*`, `**/vite.config.*`
- Entry points: `**/main.*`, `**/index.*`, `**/app.*`, `**/server.*`

### Step 2: Detect Languages and Frameworks

Check dependency files for frameworks:

- **JS/TS**: React, Vue, Express, NestJS, Jest, Vitest, Prisma
- **Python**: Django, Flask, FastAPI, pytest
- **Other**: Cargo.toml (Rust), go.mod (Go), *.csproj (.NET)

### Step 3: Identify Patterns

Use Grep to find:

- API patterns: `app\.(get|post|put|delete)\(`
- Database patterns: `prisma\.`, `mongoose\.`
- Testing patterns: `(describe|it|test)\(`
- State management: `(useContext|createStore)`

### Step 4: Generate STACK.md

Create `.tiki/STACK.md` with sections:

- **Languages**: Table with language, version, usage
- **Frontend/Backend**: Technology tables with version, purpose
- **Testing**: Test tools and their purposes
- **DevOps**: Containerization, CI/CD, deployment
- **Key Dependencies**: Production and development deps
- **Architecture Notes**: Patterns, API style, auth approach

Include auto-generated timestamp in header.

### Step 5: Generate CONCERNS.md

Analyze for issues using Grep:

- TODO/FIXME comments: `(TODO|FIXME|HACK|XXX):`
- Large files (complexity indicator)
- Hardcoded values: `(localhost|password|secret)`
- Missing error handling patterns

Create `.tiki/CONCERNS.md` with sections:

- **Tech Debt**: Location, issue, severity, notes
- **Security Concerns**: Location, issue, severity
- **Architecture Issues**: Circular deps, god objects
- **Fragile Areas**: Areas needing extra care
- **Missing Tests**: Coverage gaps by risk level
- **Recommendations**: Immediate, short-term, long-term

### Optional Documentation

Load conditional prompts based on flags:

1. If `--conventions` or `--all-docs`:
   - Read `.tiki/prompts/map-codebase/conventions-doc.md`
   - Follow instructions to generate CONVENTIONS.md

2. If `--testing` or `--all-docs`:
   - Read `.tiki/prompts/map-codebase/testing-doc.md`
   - Follow instructions to generate TESTING.md

3. If `--integrations` or `--all-docs`:
   - Read `.tiki/prompts/map-codebase/integrations-doc.md`
   - Follow instructions to generate INTEGRATIONS.md

4. If `--update-claude`:
   - Read `.tiki/prompts/map-codebase/claude-update.md`
   - Follow instructions to update CLAUDE.md

### Step 6: Display Summary

Show summary of generated files:

- List all generated files with descriptions
- Key findings: Stack summary, concerns count, severity breakdown
- Include optional doc summaries only if generated
- Recommendations based on findings
- Paths to view full reports

## Refresh Mode

If `.tiki/STACK.md` or `.tiki/CONCERNS.md` exist, offer options:

1. Regenerate (overwrite)
2. Update only (merge new findings)
3. Show diff
4. Cancel

## Integration

- `/tiki:assess-code` uses STACK.md for context
- `/tiki:create-issues` creates issues from CONCERNS.md
- `/tiki:plan-issue` references TESTING.md for TDD
- `/tiki:execute` sub-agents reference CONVENTIONS.md, INTEGRATIONS.md
