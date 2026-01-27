---
type: prompt
name: tiki:test-creator
description: Create tests following TDD workflow. Supports before (TDD), after, ask, or never modes based on config.
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
argument-hint: [--mode before|after|ask|never] [--framework jest|vitest|pytest|go|dotnet|auto]
---

# Test Creator

Create tests for code changes following the configured TDD workflow. Supports writing tests before implementation (true TDD), after implementation, or prompting the user for preference.

## Usage

```
/tiki:test-creator                           # Use config settings
/tiki:test-creator --mode before             # Force TDD mode (tests first)
/tiki:test-creator --mode after              # Force tests after implementation
/tiki:test-creator --mode ask                # Prompt for preference
/tiki:test-creator --mode never              # Skip test creation
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

If command-line flags are provided, they override config settings.

### Step 2: Detect Test Framework

If `testFramework` is "auto-detect", determine the framework:

```bash
# Check for JavaScript/TypeScript test frameworks
ls package.json 2>/dev/null && cat package.json | grep -E "(jest|vitest|mocha|ava)" || true

# Check for Python test frameworks
ls pyproject.toml setup.py requirements.txt 2>/dev/null && grep -E "(pytest|unittest|nose)" pyproject.toml setup.py requirements.txt 2>/dev/null || true

# Check for Go test files
ls *_test.go 2>/dev/null || true

# Check for Rust test configuration
ls Cargo.toml 2>/dev/null && grep "\[dev-dependencies\]" Cargo.toml || true

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
Test creation is disabled in config.
Proceeding without tests.
```
Exit early - no tests will be created.

#### Mode: "before" or "after"
Continue to appropriate workflow below.

### Step 4a: TDD Workflow (mode: "before")

When writing tests first:

#### 4a.1: Analyze the Code to Be Written

Read the current phase or task description:
- What functionality needs to be implemented?
- What are the inputs and outputs?
- What edge cases should be handled?
- What errors should be thrown?

#### 4a.2: Create Test File

Determine test file location based on framework conventions:

| Framework | Test Location Pattern |
|-----------|----------------------|
| jest | `__tests__/` or `*.test.ts` or `*.spec.ts` |
| vitest | `__tests__/` or `*.test.ts` or `*.spec.ts` |
| pytest | `tests/` or `test_*.py` or `*_test.py` |
| go test | `*_test.go` in same package |
| cargo test | `tests/` or `#[cfg(test)]` module |
| dotnet test | `*.Tests/` project or `*.Tests.csproj` |

#### 4a.3: Write Failing Tests

Create tests that:
1. Import the module/function that WILL exist (doesn't yet)
2. Test the expected behavior
3. Cover edge cases and error conditions
4. Use descriptive test names

**Example (Jest/Vitest):**
```typescript
import { calculateTotal } from '../src/utils/pricing';

describe('calculateTotal', () => {
  it('should sum item prices correctly', () => {
    const items = [{ price: 10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(30);
  });

  it('should apply discount when provided', () => {
    const items = [{ price: 100 }];
    expect(calculateTotal(items, 0.1)).toBe(90);
  });

  it('should throw on negative prices', () => {
    const items = [{ price: -10 }];
    expect(() => calculateTotal(items)).toThrow('Invalid price');
  });

  it('should return 0 for empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });
});
```

**Example (pytest):**
```python
import pytest
from src.utils.pricing import calculate_total

def test_sum_item_prices():
    items = [{"price": 10}, {"price": 20}]
    assert calculate_total(items) == 30

def test_apply_discount():
    items = [{"price": 100}]
    assert calculate_total(items, discount=0.1) == 90

def test_negative_price_raises():
    items = [{"price": -10}]
    with pytest.raises(ValueError, match="Invalid price"):
        calculate_total(items)

def test_empty_array_returns_zero():
    assert calculate_total([]) == 0
```

**Example (xUnit/.NET):**
```csharp
using Xunit;
using MyApp.Utils;

namespace MyApp.Tests.Utils;

public class PricingTests
{
    [Fact]
    public void CalculateTotal_ShouldSumItemPricesCorrectly()
    {
        // Arrange
        var items = new[] { new Item { Price = 10 }, new Item { Price = 20 } };

        // Act
        var result = Pricing.CalculateTotal(items);

        // Assert
        Assert.Equal(30, result);
    }

    [Fact]
    public void CalculateTotal_ShouldApplyDiscountWhenProvided()
    {
        var items = new[] { new Item { Price = 100 } };
        Assert.Equal(90, Pricing.CalculateTotal(items, discount: 0.1m));
    }

    [Fact]
    public void CalculateTotal_ShouldThrowOnNegativePrices()
    {
        var items = new[] { new Item { Price = -10 } };
        Assert.Throws<ArgumentException>(() => Pricing.CalculateTotal(items));
    }

    [Fact]
    public void CalculateTotal_ShouldReturnZeroForEmptyArray()
    {
        Assert.Equal(0, Pricing.CalculateTotal(Array.Empty<Item>()));
    }
}
```

#### 4a.4: Run Tests to Confirm Failure

Execute tests to verify they fail (as expected):

```bash
# Jest
npx jest path/to/test.test.ts --no-coverage 2>&1 | head -50

# Vitest
npx vitest run path/to/test.test.ts 2>&1 | head -50

# Pytest
pytest tests/test_file.py -v 2>&1 | head -50

# Go
go test ./path/to/package -v 2>&1 | head -50

# .NET (xUnit/NUnit/MSTest)
dotnet test path/to/TestProject.Tests.csproj --filter "FullyQualifiedName~ClassName" -v n 2>&1 | head -50
```

Expected output should show failures like:
- "Cannot find module" (module doesn't exist yet)
- "undefined is not a function" (function doesn't exist)
- Test assertion failures

#### 4a.5: Signal Ready for Implementation

```
## TDD Tests Created

Created test file: `path/to/test.test.ts`
Framework: jest
Tests written: 4

### Test Summary
- calculateTotal: sum item prices correctly
- calculateTotal: apply discount when provided
- calculateTotal: throw on negative prices
- calculateTotal: return 0 for empty array

### Test Run Results
All 4 tests FAILED (expected - implementation pending)

---
**Ready for Implementation**

The failing tests define the expected behavior.
Implement the code to make these tests pass.

When implementation is complete, run:
```
npx jest path/to/test.test.ts
```
```

### Step 4b: Post-Implementation Workflow (mode: "after")

When writing tests after implementation:

#### 4b.1: Analyze Implemented Code

Read the files that were just implemented:
```bash
# Find recently modified files
git diff --name-only HEAD~1 2>/dev/null || git status --short
```

For each modified file:
- What functions/methods were added?
- What are the public interfaces?
- What edge cases exist in the code?

#### 4b.2: Create Test File

Follow same location conventions as 4a.2.

#### 4b.3: Write Comprehensive Tests

Create tests that:
1. Cover all public functions/methods
2. Test the actual implementation behavior
3. Include edge cases observed in code
4. Test error handling paths

#### 4b.4: Run Tests to Confirm Pass

Execute tests and verify they pass:

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
1. Check if tests are correctly written
2. Check if implementation has bugs
3. Report failures to user

#### 4b.5: Report Results

```
## Tests Created

Created test file: `path/to/test.test.ts`
Framework: jest
Tests written: 4

### Test Summary
- calculateTotal: sum item prices correctly
- calculateTotal: apply discount when provided
- calculateTotal: throw on negative prices
- calculateTotal: return 0 for empty array

### Test Run Results
All 4 tests PASSED

---
Test coverage added for implemented code.
```

## Test File Templates

### Jest/Vitest Template

```typescript
import { describe, it, expect } from 'vitest'; // or remove for Jest

import { functionName } from '../src/path/to/module';

describe('functionName', () => {
  describe('basic functionality', () => {
    it('should handle normal input', () => {
      // Arrange
      const input = {};

      // Act
      const result = functionName(input);

      // Assert
      expect(result).toBe(expected);
    });
  });

  describe('edge cases', () => {
    it('should handle empty input', () => {
      expect(functionName(null)).toBe(defaultValue);
    });

    it('should throw on invalid input', () => {
      expect(() => functionName(invalid)).toThrow();
    });
  });
});
```

### Pytest Template

```python
import pytest
from src.module import function_name

class TestFunctionName:
    """Tests for function_name"""

    def test_basic_functionality(self):
        """Should handle normal input"""
        # Arrange
        input_data = {}

        # Act
        result = function_name(input_data)

        # Assert
        assert result == expected

    def test_empty_input(self):
        """Should handle empty input"""
        assert function_name(None) == default_value

    def test_invalid_input_raises(self):
        """Should raise on invalid input"""
        with pytest.raises(ValueError):
            function_name(invalid)
```

### Go Test Template

```go
package mypackage

import (
    "testing"
)

func TestFunctionName(t *testing.T) {
    t.Run("basic functionality", func(t *testing.T) {
        // Arrange
        input := Input{}

        // Act
        result := FunctionName(input)

        // Assert
        if result != expected {
            t.Errorf("got %v, want %v", result, expected)
        }
    })

    t.Run("edge case - empty input", func(t *testing.T) {
        result := FunctionName(nil)
        if result != defaultValue {
            t.Errorf("got %v, want %v", result, defaultValue)
        }
    })
}
```

### xUnit (.NET) Template

```csharp
using Xunit;

namespace MyApp.Tests;

public class FunctionNameTests
{
    [Fact]
    public void FunctionName_ShouldHandleNormalInput()
    {
        // Arrange
        var input = new InputType();

        // Act
        var result = ClassName.FunctionName(input);

        // Assert
        Assert.Equal(expected, result);
    }

    [Fact]
    public void FunctionName_ShouldHandleEmptyInput()
    {
        Assert.Equal(defaultValue, ClassName.FunctionName(null));
    }

    [Fact]
    public void FunctionName_ShouldThrowOnInvalidInput()
    {
        Assert.Throws<ArgumentException>(() => ClassName.FunctionName(invalid));
    }

    [Theory]
    [InlineData(1, 2)]
    [InlineData(2, 4)]
    [InlineData(3, 6)]
    public void FunctionName_ShouldDoubleValue(int input, int expected)
    {
        Assert.Equal(expected, ClassName.FunctionName(input));
    }
}
```

### NUnit (.NET) Template

```csharp
using NUnit.Framework;

namespace MyApp.Tests;

[TestFixture]
public class FunctionNameTests
{
    [Test]
    public void FunctionName_ShouldHandleNormalInput()
    {
        // Arrange
        var input = new InputType();

        // Act
        var result = ClassName.FunctionName(input);

        // Assert
        Assert.That(result, Is.EqualTo(expected));
    }

    [Test]
    public void FunctionName_ShouldHandleEmptyInput()
    {
        Assert.That(ClassName.FunctionName(null), Is.EqualTo(defaultValue));
    }

    [Test]
    public void FunctionName_ShouldThrowOnInvalidInput()
    {
        Assert.Throws<ArgumentException>(() => ClassName.FunctionName(invalid));
    }

    [TestCase(1, 2)]
    [TestCase(2, 4)]
    [TestCase(3, 6)]
    public void FunctionName_ShouldDoubleValue(int input, int expected)
    {
        Assert.That(ClassName.FunctionName(input), Is.EqualTo(expected));
    }
}
```

## Examples

### Example 1: TDD Mode (before)

```
User: /tiki:test-creator --mode before

Claude: ## TDD Mode Active

I'll analyze the current task and write failing tests first.

### Current Task Analysis
From the phase description, I need to create tests for a `validateEmail` function that:
- Validates email format
- Returns true for valid emails
- Returns false for invalid emails
- Handles edge cases (empty string, null)

### Detecting Test Framework
Found: vitest in package.json

### Creating Test File

Creating `src/utils/__tests__/validateEmail.test.ts`:

[Creates test file with failing tests]

### Running Tests

$ npx vitest run src/utils/__tests__/validateEmail.test.ts

FAIL  src/utils/__tests__/validateEmail.test.ts
  validateEmail
    ✗ should return true for valid email
    ✗ should return false for invalid format
    ✗ should return false for empty string
    ✗ should return false for null

Tests: 4 failed, 4 total

---
**Tests Created - Ready for Implementation**

The tests define the expected behavior for `validateEmail`.
Now implement `src/utils/validateEmail.ts` to make them pass.
```

### Example 2: After Mode

```
User: /tiki:test-creator --mode after

Claude: ## Writing Tests for Implemented Code

### Analyzing Recent Changes
Files modified:
- src/utils/validateEmail.ts (new)

### Reading Implementation
[Reads the file and understands the logic]

### Creating Test File

Creating `src/utils/__tests__/validateEmail.test.ts`:

[Creates comprehensive tests based on implementation]

### Running Tests

$ npx vitest run src/utils/__tests__/validateEmail.test.ts

PASS  src/utils/__tests__/validateEmail.test.ts
  validateEmail
    ✓ should return true for valid email
    ✓ should return false for invalid format
    ✓ should return false for empty string
    ✓ should handle null gracefully

Tests: 4 passed, 4 total

---
**Tests Created and Passing**

Test coverage has been added for the implemented code.
```

### Example 3: Ask Mode

```
User: /tiki:test-creator

Claude: ## Test Creation Mode

Your config has `createTests: "ask"`.

How would you like to handle testing?

1. **before** (TDD) - Write failing tests first, then implement
2. **after** - Implement first, then write tests
3. **never** - Skip test creation for this task

User: 1

Claude: ## TDD Mode Active
[Continues with TDD workflow...]
```

## Integration with Execute

The test-creator can be invoked automatically during phase execution:

1. `/tiki:execute` reads config
2. If `testing.createTests` is "before":
   - Before each phase, spawn test-creator to write tests
   - Then spawn phase sub-agent to implement
   - Verify tests pass after implementation
3. If `testing.createTests` is "after":
   - Spawn phase sub-agent to implement
   - Then spawn test-creator to write tests
   - Verify tests pass

## Error Handling

### No Test Framework Detected
```
Could not auto-detect test framework.
Please specify with --framework or set testing.testFramework in .tiki/config.json

Supported frameworks: jest, vitest, pytest, go, mocha, cargo, dotnet
```

### Test Run Failed (unexpected)
```
Tests failed unexpectedly.

Expected: Tests to [pass|fail]
Actual: [opposite result]

Please review the test output and:
- Check test assertions are correct
- Verify implementation matches expected behavior
- Fix any bugs in implementation or tests
```

### Missing Dependencies
```
Test framework 'jest' is not installed.

Run: npm install --save-dev jest @types/jest
```

## Notes

- Test files follow project conventions (check existing test files for patterns)
- TDD tests should be minimal - just enough to define behavior
- After-implementation tests can be more comprehensive
- Always run tests after creation to verify they work
- The test-creator respects the project's existing test structure
