# TDD Workflow (mode: "before")

Write failing tests before implementation.

## Step 1: Analyze Code to Be Written

From the phase/task description, identify:
- Functionality to implement
- Inputs and outputs
- Edge cases to handle
- Expected errors

## Step 2: Create Test File

Use framework-specific location conventions:

| Framework | Test Location |
|-----------|---------------|
| jest/vitest | `__tests__/` or `*.test.ts` |
| pytest | `tests/` or `test_*.py` |
| go test | `*_test.go` (same package) |
| dotnet | `*.Tests/` project |

## Step 3: Write Failing Tests

Create tests that:
1. Import the module that WILL exist
2. Test expected behavior
3. Cover edge cases and errors
4. Use descriptive names

**Jest/Vitest Example:**
```typescript
import { calculateTotal } from '../src/utils/pricing';

describe('calculateTotal', () => {
  it('should sum prices', () => {
    expect(calculateTotal([{price: 10}, {price: 20}])).toBe(30);
  });
  it('should throw on negative', () => {
    expect(() => calculateTotal([{price: -1}])).toThrow();
  });
});
```

**Pytest Example:**
```python
from src.utils.pricing import calculate_total
import pytest

def test_sum_prices():
    assert calculate_total([{"price": 10}, {"price": 20}]) == 30

def test_negative_raises():
    with pytest.raises(ValueError):
        calculate_total([{"price": -1}])
```

## Step 4: Run Tests to Confirm Failure

```bash
# Jest
npx jest path/to/test.test.ts --no-coverage 2>&1 | head -50

# Vitest
npx vitest run path/to/test.test.ts 2>&1 | head -50

# Pytest
pytest tests/test_file.py -v 2>&1 | head -50

# Go
go test ./path/to/package -v 2>&1 | head -50

# .NET
dotnet test path/to/TestProject.Tests.csproj -v n 2>&1 | head -50
```

Expected failures: "Cannot find module", "undefined is not a function", assertion errors.

## Step 5: Signal Ready

Report:
```
## TDD Tests Created

Created: `path/to/test.test.ts`
Framework: [framework]
Tests: [count]

### Tests
- [test name 1]
- [test name 2]

All tests FAILED (expected - implementation pending)

**Ready for Implementation**
```
