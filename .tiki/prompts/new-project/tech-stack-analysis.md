# Tech Stack Analysis

Instructions for detecting and recommending tech stack when an existing codebase is present.

## When to Use

Load this prompt when:
- Files exist in the project root (not a greenfield project)
- User answers "No preference - recommend based on goals"
- Detecting existing patterns to suggest consistent additions

## Detection Steps

### 1. Check for Package Manifests

Search for these files to identify the tech stack:

| File | Indicates |
|------|-----------|
| `package.json` | Node.js/JavaScript/TypeScript |
| `requirements.txt` / `pyproject.toml` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` | Java/Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |

### 2. Infer Frameworks

From package.json dependencies:
- `react` / `next` / `vue` / `svelte` - Frontend framework
- `express` / `fastify` / `hono` - Node backend
- `prisma` / `drizzle` / `typeorm` - Database ORM
- `vitest` / `jest` / `mocha` - Test framework

From Python dependencies:
- `fastapi` / `flask` / `django` - Web framework
- `pytest` / `unittest` - Test framework
- `sqlalchemy` / `django-orm` - Database ORM

### 3. Detect Patterns

Look for existing conventions:
- Folder structure (`src/`, `lib/`, `app/`)
- Config files (`.eslintrc`, `tsconfig.json`, `ruff.toml`)
- Test locations (`tests/`, `__tests__/`, `*.test.ts`)

### 4. Recommendation Format

Present detected stack to user:

```
I detected the following tech stack:
- Language: {detected}
- Framework: {detected}
- Database: {detected or "not detected"}
- Testing: {detected or "not detected"}

Should I use these for the project context, or would you like to specify something different?
```

## Consistency Guidelines

When suggesting additions to existing codebases:
- Match existing language version (e.g., Node 18 if package.json specifies)
- Use same test framework for new tests
- Follow existing folder structure patterns
- Respect existing linting/formatting config
