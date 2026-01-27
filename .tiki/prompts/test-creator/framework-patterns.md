# Framework-Specific Test Patterns

## Test File Locations

| Framework | Location Pattern |
|-----------|------------------|
| jest | `__tests__/` or `*.test.ts` or `*.spec.ts` |
| vitest | `__tests__/` or `*.test.ts` or `*.spec.ts` |
| pytest | `tests/` or `test_*.py` or `*_test.py` |
| go test | `*_test.go` in same package |
| cargo test | `tests/` or `#[cfg(test)]` module |
| dotnet | `*.Tests/` project or `*.Tests.csproj` |

## Jest/Vitest Template

```typescript
import { functionName } from '../src/path/to/module';

describe('functionName', () => {
  it('should handle normal input', () => {
    expect(functionName(input)).toBe(expected);
  });

  it('should handle empty input', () => {
    expect(functionName(null)).toBe(defaultValue);
  });

  it('should throw on invalid input', () => {
    expect(() => functionName(invalid)).toThrow();
  });
});
```

## Pytest Template

```python
import pytest
from src.module import function_name

def test_normal_input():
    assert function_name(input_data) == expected

def test_empty_input():
    assert function_name(None) == default_value

def test_invalid_raises():
    with pytest.raises(ValueError):
        function_name(invalid)
```

## Go Template

```go
package mypackage

import "testing"

func TestFunctionName(t *testing.T) {
    t.Run("normal input", func(t *testing.T) {
        result := FunctionName(input)
        if result != expected {
            t.Errorf("got %v, want %v", result, expected)
        }
    })
}
```

## xUnit (.NET) Template

```csharp
using Xunit;

public class FunctionNameTests
{
    [Fact]
    public void FunctionName_NormalInput_ReturnsExpected()
    {
        Assert.Equal(expected, ClassName.FunctionName(input));
    }

    [Fact]
    public void FunctionName_InvalidInput_Throws()
    {
        Assert.Throws<ArgumentException>(() => ClassName.FunctionName(invalid));
    }

    [Theory]
    [InlineData(1, 2)]
    [InlineData(2, 4)]
    public void FunctionName_Parameterized(int input, int expected)
    {
        Assert.Equal(expected, ClassName.FunctionName(input));
    }
}
```

## NUnit (.NET) Template

```csharp
using NUnit.Framework;

[TestFixture]
public class FunctionNameTests
{
    [Test]
    public void FunctionName_NormalInput_ReturnsExpected()
    {
        Assert.That(ClassName.FunctionName(input), Is.EqualTo(expected));
    }

    [Test]
    public void FunctionName_InvalidInput_Throws()
    {
        Assert.Throws<ArgumentException>(() => ClassName.FunctionName(invalid));
    }

    [TestCase(1, 2)]
    [TestCase(2, 4)]
    public void FunctionName_Parameterized(int input, int expected)
    {
        Assert.That(ClassName.FunctionName(input), Is.EqualTo(expected));
    }
}
```
