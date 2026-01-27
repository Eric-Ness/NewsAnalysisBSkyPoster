---
type: prompt
name: tiki:test-creator
description: Create tests following TDD workflow. Supports before (TDD), after, ask, or never modes based on config.
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
argument-hint: [--mode before|after|ask|never] [--framework jest|vitest|pytest|go|dotnet|auto]
---

# Test Creator

Create tests for code changes following the configured TDD workflow.

## Usage

```
/tiki:test-creator                           # Use config settings
/tiki:test-creator --mode before             # Force TDD mode (tests first)
/tiki:test-creator --mode after              # Force tests after implementation
/tiki:test-creator --framework pytest        # Force specific framework
```

## Instructions

### Step 1: Read Configuration

Check `.tiki/config.json` for testing settings:

```bash
cat .tiki/config.json 2>/dev/null || echo "{}"
```

Extract settings:
- `testing.createTests`: "before" | "after" | "ask" | "never" (default: "ask")
- `testing.testFramework`: framework name or "auto-detect" (default: "auto-detect")

Command-line flags override config settings.

### Step 2: Detect Test Framework

If `testFramework` is "auto-detect", determine the framework:

```bash
# Check for JavaScript/TypeScript test frameworks
ls package.json 2>/dev/null && cat package.json | grep -E "(jest|vitest|mocha|ava)" || true

# Check for Python test frameworks
ls pyproject.toml setup.py requirements.txt 2>/dev/null && grep -E "(pytest|unittest|nose)" pyproject.toml setup.py requirements.txt 2>/dev/null || true

# Check for Go test files
ls *_test.go 2>/dev/null || true

# Check for .NET test projects
ls *.csproj *.sln 2>/dev/null && grep -l "Microsoft.NET.Test.Sdk\|xunit\|NUnit\|MSTest" *.csproj */*.csproj 2>/dev/null || true
```

**Framework Detection Priority:**

| Indicator | Framework |
|-----------|-----------|
| `vitest` in package.json | vitest |
| `jest` in package.json | jest |
| `mocha` in package.json | mocha |
| `pytest` in pyproject.toml/requirements | pytest |
| `*_test.go` files exist | go test |
| `Cargo.toml` exists | cargo test |
| `*.csproj` with test SDK | dotnet test |
| None detected | Prompt user |

### Step 3: Determine Test Mode

Based on `createTests` setting:

#### Mode: "ask"
Prompt the user:
```
How would you like to handle testing?

1. **before** (TDD) - Write failing tests first, then implement
2. **after** - Implement first, then write tests
3. **never** - Skip test creation for this task

Your choice (1/2/3):
```

#### Mode: "never"
```
Test creation is disabled in config. Proceeding without tests.
```
Exit early - no tests will be created.

#### Mode: "before" or "after"
Continue to appropriate workflow below.

### Step 4a: TDD Workflow (mode: "before")

Read `.tiki/prompts/test-creator/tdd-before.md` and follow that workflow.

For framework-specific test templates, read `.tiki/prompts/test-creator/framework-patterns.md`.

### Step 4b: Post-Implementation Workflow (mode: "after")

Read `.tiki/prompts/test-creator/after-mode.md` and follow that workflow.

For framework-specific test templates, read `.tiki/prompts/test-creator/framework-patterns.md`.

## Error Handling

- **No framework detected**: Prompt user to specify `--framework` or set `testing.testFramework` in config
- **Test run failed unexpectedly**: Review test output, check assertions, verify implementation matches expected behavior
- **Missing dependencies**: Report framework not installed with install command (e.g., `npm install --save-dev jest`)

## Notes

- Test files follow project conventions - check existing test files for patterns
- TDD tests should be minimal - just enough to define behavior
- After-implementation tests can be more comprehensive
- Always run tests after creation to verify they work
