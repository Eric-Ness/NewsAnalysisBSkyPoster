# Post-Implementation Workflow (mode: "after")

Write tests after code is implemented.

## Step 1: Analyze Implemented Code

Find recently modified files:
```bash
git diff --name-only HEAD~1 2>/dev/null || git status --short
```

For each file, identify:
- Added functions/methods
- Public interfaces
- Edge cases in the code

## Step 2: Create Test File

Follow framework location conventions:
- jest/vitest: `__tests__/` or `*.test.ts`
- pytest: `tests/` or `test_*.py`
- go: `*_test.go` (same package)
- dotnet: `*.Tests/` project

## Step 3: Write Comprehensive Tests

Create tests that:
1. Cover all public functions
2. Test actual implementation behavior
3. Include observed edge cases
4. Test error handling paths

## Step 4: Run Tests to Confirm Pass

```bash
# Jest
npx jest path/to/test.test.ts

# Vitest
npx vitest run path/to/test.test.ts

# Pytest
pytest tests/test_file.py -v

# Go
go test ./path/to/package -v

# .NET
dotnet test path/to/TestProject.Tests.csproj -v n
```

If tests fail:
1. Check test correctness
2. Check for implementation bugs
3. Report failures to user

## Step 5: Report Results

```
## Tests Created

Created: `path/to/test.test.ts`
Framework: [framework]
Tests: [count]

### Tests
- [test name 1]
- [test name 2]

All tests PASSED

Test coverage added for implemented code.
```
