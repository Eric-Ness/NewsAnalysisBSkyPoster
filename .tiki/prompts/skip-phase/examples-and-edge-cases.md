# Skip Phase: Examples and Edge Cases

Reference this document for edge case handling and usage examples.

## Edge Cases

### Skipping Last Phase

If skipping the final phase:

```
Phase 4 skipped.

All phases complete for Issue #34:
  1. Setup project structure [completed]
  2. Add authentication [completed]
  3. Add user dashboard [completed]
  4. Write tests [skipped]

Issue execution complete. Review with `/tiki:state`.
```

### Skipping Multiple Phases

To skip multiple phases, run the command multiple times:

```
/tiki:skip-phase 2
/tiki:skip-phase 3
```

Range skipping is not supported:
```
Skipping phases 2-3 is not directly supported.
Please skip one phase at a time to ensure intentional progression.
```

### No Reason Provided

If no reason provided, prompt but do not require:

```
No skip reason provided.

Tip: Add a reason for future reference:
  /tiki:skip-phase 2 --reason "Already done manually"

Proceeding without reason...

Phase 2 skipped.
```

## Examples

### Example 1: Skip Current Phase

```
> /tiki:skip-phase --current

Skipping Phase 2: Add authentication

Phase 2 skipped.

**Reason**: No reason provided
**Next**: Phase 3 - Add user dashboard

Continue with `/tiki:execute 34`.
```

### Example 2: Skip with Reason

```
> /tiki:skip-phase 3 --reason "Feature deprioritized for MVP"

Skipping Phase 3: Add user dashboard

Phase 3 skipped.

**Reason**: Feature deprioritized for MVP
**Next**: Phase 4 - Write tests

Continue with `/tiki:execute 34`.
```

## Integration with Other Skills

- **`/tiki:execute`**: After skipping, use `/tiki:execute` to continue from next phase
- **`/tiki:heal`**: Use heal instead of skip for failed phases you want to fix
- **`/tiki:redo-phase`**: Use redo to repeat a completed or skipped phase
- **`/tiki:state`**: View current status including skipped phases
- **`/tiki:pause`**: Pause instead of skip if you want to return later
