# TDD Workflow

Conditional prompt loaded when `config.testing.createTests` is "before".

## Red Phase - Write Failing Tests

Spawn test-creator sub-agent before implementation:

```text
Task tool call:
- subagent_type: "general-purpose"
- prompt: <TDD test creation prompt below>
- description: "Write failing tests for Phase N"
```

### Test Creation Prompt

```text
Create failing tests for Phase {N}: {phase_title}

## Context
{phase_content}
{files_to_create_or_modify}

## Requirements
1. Detect test framework (see table below)
2. Create test file following project conventions
3. Write tests covering: happy path, edge cases, error handling
4. Tests MUST fail initially (code not yet implemented)
5. Run tests to confirm failure

## Framework Detection

| Indicator | Framework | Run Command |
|-----------|-----------|-------------|
| `vitest` in package.json | vitest | `npx vitest run` |
| `jest` in package.json | jest | `npx jest --no-coverage` |
| `mocha` in package.json | mocha | `npx mocha` |
| `pytest` in requirements | pytest | `pytest -v` |
| `*_test.go` files | go test | `go test -v ./...` |
| `Cargo.toml` | cargo test | `cargo test` |
| `*.csproj` with test SDK | dotnet | `dotnet test` |

## Output
Report: test file path, framework used, test count, failure confirmation.
End with: SUMMARY: Created N failing tests for [functionality]
```

## Green Phase - Implementation

After tests created, the main phase sub-agent implements code to make tests pass.

Sub-agent receives TDD context:
```text
## TDD Context
Failing tests exist at: {test_file_path}
Framework: {detected_framework}
Run command: {test_command}

Implement code to make all tests pass. Do not modify the tests.
```

## Verification

After implementation, verify tests pass:

```bash
# Run framework-appropriate command
npx vitest run path/to/test 2>&1 | head -50  # vitest
npx jest path/to/test --no-coverage 2>&1 | head -50  # jest
pytest tests/test_file.py -v 2>&1 | head -50  # pytest
go test ./path/... -v 2>&1 | head -50  # go
dotnet test --filter "Name~Test" 2>&1 | head -50  # dotnet
```

### Pass/Fail Handling

**On Pass:** Continue to next phase. Report: "TDD: All N tests passing."

**On Fail:**
1. If auto-fix enabled: attempt fix (max 3 tries)
2. Record failure reason
3. If exhausted: pause for manual intervention

## Integration Points

- Execute Step 4d: Load this prompt when `createTests: "before"`
- Execute Step 4h: For "after" mode, spawn test-creator post-implementation
- Sub-agent prompt: Include TDD context section when tests exist
