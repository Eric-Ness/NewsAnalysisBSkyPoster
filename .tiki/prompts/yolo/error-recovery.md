# Error Recovery

Handle failures at each stage of the YOLO workflow.

## Issue Not Found

```text
[1/7] Fetching issue... FAILED

Issue #<number> not found.

Verify the issue number exists:
  gh issue list

Or check if you're in the correct repository.
```

**Stop execution.**

## Planning Failure

```text
[3/7] Creating plan... FAILED

Failed to create execution plan.

Possible causes:
- Issue description is unclear or empty
- Codebase analysis encountered errors

Try:
- `/tiki:plan-issue <number>` for manual planning
- Review the issue description for clarity
```

**Stop execution.**

## Audit Blocking Errors

```text
[4/7] Auditing plan... BLOCKED

The plan has blocking issues that prevent execution:

Errors:
- <error 1 description>
- <error 2 description>

Resolution required. Run `/tiki:plan-issue <number>` to revise.
```

**Stop execution.**

## Execution Failure

```text
[5/7] Executing phases... FAILED at Phase <N>

Phase <N> of <total> failed: <title>

Error: <error description>

Progress saved. Phases 1-<N-1> completed successfully.

Options:
- Auto-heal: `/tiki:heal` - attempts automatic fix
- Manual fix: Fix error, then `/tiki:execute <number> --from <N>`
- Skip phase: `/tiki:skip-phase <N>`

Queue review skipped due to execution failure.
```

**Stop execution. Do not proceed to queue review.**

## Ship Failure

```text
[7/7] Shipping... FAILED

<error description>

The issue was NOT closed. Options:
- Fix the issue and run `/tiki:ship` manually
- View state: `/tiki:state`
```

## Recovery Options Summary

| Stage | Failure | Recovery |
|-------|---------|----------|
| Fetch | Not found | Check issue number, repo |
| Review | Blocked | Address concerns or --force-review |
| Plan | Failed | Manual `/tiki:plan-issue` |
| Audit | Blocked | Revise plan |
| Execute | Phase N failed | `/tiki:heal` or `--from N` |
| Ship | Failed | Manual `/tiki:ship` |

## Cleanup After Failure

Run cleanup silently:

```bash
rm -f ./tmpclaude-* ./nul ./NUL 2>/dev/null || true
rm -f .tiki/tmp-* .tiki/*.tmp 2>/dev/null || true
```
