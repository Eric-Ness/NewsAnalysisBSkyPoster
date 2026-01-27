# Review Stage

Analyze the issue for concerns before planning. Same logic as `/tiki:review-issue --yolo`.

## Instructions

1. **Analyze the issue** for:
   - Alternatives to consider
   - Assumptions that need validation
   - Potential blockers
   - Edge cases to handle
   - Scope clarity
   - Security/risk concerns

2. **Explore codebase** if needed (relevant files, existing patterns)

3. **Categorize findings** by severity:
   - **blocking**: Must be resolved before planning
   - **warning**: Should be considered but can proceed
   - **info**: Informational, no action needed

4. **Determine verdict**: `blocked`, `warnings`, or `clean`

## Verdict Handling

### Blocked (AND `--force-review` NOT set)

```text
[2/7] Reviewing issue... BLOCKED

### Blocking Concerns Found

1. **[Category]**: Description
   - Detail 1
   - Detail 2

These concerns must be addressed before planning can proceed.

### Options
- Address concerns and retry: `/tiki:yolo <number>`
- Override: `/tiki:yolo <number> --force-review`
- Skip review: `/tiki:yolo <number> --skip-review`

YOLO mode paused.
```

**STOP execution. Do not proceed to planning.**

### Blocked (AND `--force-review` IS set)

```text
[2/7] Reviewing issue... BLOCKED (overridden with --force-review)
      - Blocking: <concern summary>

      Proceeding despite blocking concerns (--force-review)

[3/7] Creating plan...
```

Continue to planning.

### Warnings

```text
[2/7] Reviewing issue... OK (with warnings)
      - Warning: <concern 1>
      - Warning: <concern 2>

      Proceeding despite warnings.

[3/7] Creating plan...
```

Continue to planning.

### Clean

```text
[2/7] Reviewing issue... OK (no concerns)
      Issue is well-defined, ready to plan.

[3/7] Creating plan...
```

Continue to planning.

## GitHub Comment

If concerns found, add a comment to the issue with recommendations.
