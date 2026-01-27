# TDD Handling

Test-Driven Development workflow for YOLO mode execution.

## When TDD is Enabled

Default behavior (no `--no-tdd` flag). Each phase follows Red-Green-Refactor:

### Red Phase (Before Implementation)

1. Create failing tests for the phase's functionality
2. Run tests to verify they fail as expected
3. Record test file paths for verification

### Green Phase (After Implementation)

1. Execute phase implementation
2. Run tests to verify they pass
3. Record test results

## Progress Display

```text
[5/7] Executing phases (TDD: enabled)...
      Phase 1/3: <title>... DONE
        Tests: 4 passing
      Phase 2/3: <title>... DONE
        Tests: 5 passing
        DISCOVERED: <item if any>
      Phase 3/3: <title>... DONE
        Tests: 3 passing
```

## TDD Test Failure

If tests don't pass after implementation:

```text
[5/7] Executing phases... FAILED at Phase <N> (TDD verification)

Phase <N> implementation did not pass tests.

Test Results:
  FAIL src/routes/__tests__/auth.test.ts
    - <test name> (expected <X>, got <Y>)
    - <test name> (<error message>)

Options:
- Auto-heal: `/tiki:heal` - attempts automatic fix
- Manual fix: Review and fix, then `/tiki:execute <number> --from <N>`
```

## When TDD is Disabled

With `--no-tdd` flag:

```text
[5/7] Executing phases (TDD: disabled)...
      Phase 1/2: <title>... DONE
      Phase 2/2: <title>... DONE
```

Skip test creation and verification. Use when:
- Issue is documentation or configuration only
- Tests already exist
- Faster execution needed
