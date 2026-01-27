# Release Integration

**Load Condition:** Issue is found in a release file (`.tiki/releases/*.json`).

## Purpose

Incorporate release context into planning when an issue is part of an active release, including requirements mapping.

## Step 1: Check Release Association

Search all release files in `.tiki/releases/` for this issue number:

```bash
# List release files
ls .tiki/releases/*.json

# For each file, check if issue number appears in the issues array
```

If issue found, extract:
- `version`: Release version (e.g., "v1.1")
- `status`: Release status (draft, planning, in_progress, etc.)
- `requirementsEnabled`: Whether requirements tracking is active
- `issueRequirements`: Any existing requirement mappings for this issue
- `githubMilestone`: Associated milestone URL

## Step 2: Store Release Context

```json
{
  "hasRelease": true,
  "version": "v1.1",
  "requirementsEnabled": true,
  "issueRequirements": ["CORE-01"],
  "availableRequirements": null,
  "githubMilestone": "https://github.com/owner/repo/milestone/1"
}
```

If requirements enabled, load `.tiki/requirements.json` to populate `availableRequirements`.

## Step 3: Display Release Detection

```text
## Release Context Detected

**Release:** {version}
**Status:** {status}
**GitHub Milestone:** {milestone URL or "None"}

This issue is part of release {version}.
{If requirementsEnabled: "Requirements tracking is enabled for this release."}
{If issueRequirements.length > 0: "Currently mapped to requirements: {list}"}
```

**Error handling:** If release detection fails, skip silently and continue normal planning.

## Step 4: Requirements Mapping (Step 5.7)

**Skip if:**
- `requirementsEnabled` is false
- `availableRequirements` could not be loaded

### 4a. Display Available Requirements

Present requirements from `.tiki/requirements.json` by category:

```text
## Requirements Mapping

This issue is part of release {version} with requirements tracking enabled.

**Available Requirements:**

**CORE - Core Functionality:**
- CORE-01: {requirement text}
- CORE-02: {requirement text}

**SEC - Security:**
- SEC-01: {requirement text}
```

### 4b. Suggest Requirement Mappings

Analyze success criteria and phase content to suggest mappings:

1. Compare criterion descriptions against requirement text
2. Compare phase titles/content against requirement text
3. Suggest requirements with semantic overlap

Display suggestions:
```text
**Suggested requirements based on plan analysis:**
- CORE-01: {requirement text} (matches criteria: functional-1)
- SEC-01: {requirement text} (matches phase: "Setup authentication")

Would you like to map these requirements? [y/edit/skip]
```

### 4c. Prompt for Confirmation

Options:
- **Yes (y)**: Accept suggested mappings
- **Edit**: Allow user to specify requirement IDs
- **Skip**: Continue without mapping

### 4d. Store Requirements Mapping

Add to plan:
```json
{
  "addressesRequirements": ["CORE-01", "SEC-01"],
  "release": {
    "version": "v1.1",
    "milestone": "https://github.com/owner/repo/milestone/1"
  }
}
```

**Error handling:** If any step fails, skip mapping and continue with plan.

## Step 5: Display in Final Plan

Include Release Context section at the top of Step 6 display (before Project Context):

```markdown
### Release Context

**Release:** {version}
**Milestone:** [{Milestone title}]({milestone URL}) {or "None"}
**Requirements Addressed:** {comma-separated IDs} {or "None mapped"}

---
```

**If issue NOT in a release:** Omit section entirely (silent skip).

**If release detection fails:** Omit section entirely (silent skip).
