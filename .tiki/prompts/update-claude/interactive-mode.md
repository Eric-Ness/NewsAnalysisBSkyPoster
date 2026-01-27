# Interactive Mode

Step-by-step walkthrough for `--interactive` flag.

## Introduction

```
## Update CLAUDE.md - Interactive Mode

I'll walk you through adding patterns to CLAUDE.md.
```

## Category Prompts

Walk through each category in order:

### 1. Code Conventions

```
### Step 1: Code Conventions

What naming conventions does this project use?

Examples:
- "Components are PascalCase"
- "Files are kebab-case"
- "Services end with Service.ts"

Your input (or 'skip'):
```

### 2. File Organization

```
### Step 2: File Organization

How are files and folders organized?

Examples:
- "Services in src/services/"
- "Components in src/components/"
- "Tests next to source files"

Your input (or 'skip'):
```

### 3. Testing Patterns

```
### Step 3: Testing Patterns

What testing conventions does this project follow?

Examples:
- "Use describe/it blocks"
- "Mock with MSW for API calls"
- "Page objects for E2E tests"

Your input (or 'skip'):
```

### 4. Common Gotchas

```
### Step 4: Common Gotchas

What are things to watch out for in this project?

Examples:
- "Run migrations before starting dev server"
- "Don't use X library with Y"
- "Environment variable Z must be set"

Your input (or 'skip'):
```

### 5. Key Decisions

```
### Step 5: Key Decisions

What architectural decisions should Claude know about?

Examples:
- "We use Prisma for database access"
- "Authentication uses JWT"
- "API follows REST conventions"

Your input (or 'skip'):
```

### 6. Team Preferences

```
### Step 6: Team Preferences

What style or quality preferences does the team have?

Examples:
- "Prefer early returns"
- "Use named exports"
- "No any types - use unknown"

Your input (or 'skip'):
```

## Finalization

After all categories:

1. Compile entered patterns
2. Show preview of CLAUDE.md changes
3. Ask for confirmation before applying
4. Apply changes and mark patterns synced
