# Requirement Verification

Load this prompt after all issues complete, if requirements exist and --skip-verify not provided.

## Load Requirements

```bash
if [ -f ".tiki/requirements.json" ]; then
  cat ".tiki/requirements.json"
else
  echo "NO_REQUIREMENTS"
fi
```

If no requirements file exists, skip to release shipping.

## Identify Requirements to Verify

Parse requirements addressed by this release:

```javascript
function getRequirementsForRelease(requirements, release) {
  const releaseIssueNumbers = release.issues.map(i => i.number);
  const toVerify = [];

  for (const category of requirements.categories) {
    for (const req of category.requirements) {
      const addressedByReleaseIssue = req.implementedBy?.some(
        issueNum => releaseIssueNumbers.includes(issueNum)
      );
      if (addressedByReleaseIssue && req.status !== 'verified') {
        toVerify.push({ ...req, categoryName: category.name });
      }
    }
  }
  return toVerify;
}
```

If no requirements to verify, skip to release shipping.

## Display Overview

```text
## Requirement Verification

{count} requirements to verify for release {version}:

| # | ID | Requirement | Type | Addressed By |
|---|------|-------------|------|--------------|
| {n} | {req.id} | {req.text} | {req.verification.type} | #{issues} |
```

## Auto-Verification

For requirements with auto-verifiable types (automated_test, state_check, documentation):

1. **automated_test**: Check for test files, run tests if configured
2. **state_check**: Parse verification description for file/state checks
3. **documentation**: Check if documentation files exist

Display results as verified, needs manual, or failed.

## Manual Verification

If requirements need manual verification, offer options:

```text
### Manual Verification Required

Options:
1. **Verify now** - Interactive verification for each
2. **Ship without verification** - Mark as unverified and proceed
3. **Pause and verify later** - Save state for later

Enter choice:
```

For interactive verification, present each requirement with context and ask:
- Yes - Mark as verified
- No - Mark as failed
- Skip - Leave unverified

## Update Requirements File

```javascript
if (result.status === 'verified') {
  req.status = 'verified';
  req.verifiedAt = new Date().toISOString();
  req.verificationMethod = result.method;
} else if (result.status === 'failed') {
  req.status = 'failed';
  req.verificationNotes = result.notes;
}
```

Save updated requirements.json.

## Summary

```text
### Verification Complete

| Status | Count |
|--------|-------|
| Auto-Verified | {count} |
| Manually Verified | {count} |
| Failed | {count} |
| Skipped | {count} |
```

Proceed to release shipping.
