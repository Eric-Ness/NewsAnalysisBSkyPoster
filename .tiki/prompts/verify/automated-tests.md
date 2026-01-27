# Automated Verification

Classification and execution of automatable verification items.

## Classification Rules

Analyze verification text to determine automation potential:

**File Existence** (automatable):
- Contains "exists" AND references file extension (.ts, .js, .md, .json, etc.)
- Check with Glob tool

**Content Check** (automatable):
- Contains "contains", "includes", or "has"
- Extract file and content, check with Grep tool

**Test Execution** (automatable):
- Contains "tests pass" or "test passes"
- Run appropriate test command based on project type

**Build Check** (automatable):
- Contains "builds" or "compiles"
- Run appropriate build command

**Default**: Mark as manual if no pattern matches

## Execution Logic

**File Existence:**
```
Extract path from "File X exists" or "X.ts exists"
Use Glob to check existence
Return PASS if found, FAIL if not
```

**Content Check:**
```
Extract from "X contains Y" pattern
Use Grep to search for content in file
Return PASS if found, FAIL if not
```

**Test Execution:**
Read `.tiki/config.json` for test framework, or auto-detect:
- `package.json` -> `npm test`
- `Cargo.toml` -> `cargo test`
- `go.mod` -> `go test ./...`

**Build Check:**
Similar detection:
- `package.json` -> `npm run build`
- `Cargo.toml` -> `cargo build`

## Result Display

```
### Phase N: {title}

1. [PASS] User model exists in src/models/user.ts
   Checked: File found at src/models/user.ts

2. [FAIL] Email service connects successfully
   Error: Connection timeout

3. [MANUAL] API endpoint testing
   Reason: Requires manual verification
```
