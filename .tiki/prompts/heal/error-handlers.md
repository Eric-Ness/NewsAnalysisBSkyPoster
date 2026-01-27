# Error Type Handlers

Reference tables for diagnosing common error types by pattern, cause, and fix.

## TypeScript Errors

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `Property X does not exist on type Y` | Missing type definition | Add to interface or use declaration merging |
| `Cannot find module` | Missing import or package | Add import or install package |
| `Type X is not assignable to type Y` | Type mismatch | Fix types or add type assertion |
| `Object is possibly undefined` | Null safety | Add null check or optional chaining |

## Test Failures

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `Expected X but received Y` | Logic error | Fix implementation |
| `Cannot read property of undefined` | Missing mock or setup | Add test setup |
| `Timeout` | Async issue | Add await or increase timeout |

## Build Errors

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `Module not found` | Missing dependency | npm install |
| `Syntax error` | Invalid code | Fix syntax |
| `Out of memory` | Build too large | Increase memory or split |

## Runtime Errors

| Error Pattern | Likely Cause | Common Fix |
|---------------|--------------|------------|
| `ENOENT` | File not found | Create file or fix path |
| `ECONNREFUSED` | Service not running | Start service |
| `Permission denied` | Access issue | Fix permissions |
