# Detailed Audit Output Format

Extended output format for `--verbose` flag showing comprehensive plan analysis.

## Phase Analysis Format

For each phase, display:

```
### Phase {number}: {title}
- Tasks: {count}
- Files: {count} ({comma-separated list})
- Dependencies: {list or "none"}
- Verification: {checkmark or x} ({count} steps)
- Addresses Criteria: {criterion IDs with titles}
- Estimated complexity: {Low|Medium|High}
```

Complexity estimation:
- **Low:** 1-4 tasks, 1-5 files, no dependencies
- **Medium:** 5-7 tasks, 6-10 files, 1-2 dependencies
- **High:** 8+ tasks, 11+ files, 3+ dependencies

## Dependency Graph Visualization

Display hierarchical dependency tree using ASCII art:

```
Phase 1 (Title)
    +-- Phase 2 (Title)
    |   +-- Phase 4 (Title)
    +-- Phase 3 (Title)
        +-- Phase 5 (Title)
```

For phases with no dependencies, show as root nodes.
For phases with multiple dependencies, list under each parent.

## File Modification Map

List each file with the phases that modify it:

```
## File Modification Map

src/models/user.ts: Phase 1
src/routes/auth.ts: Phase 2, Phase 3 [warning]
src/middleware/auth.ts: Phase 2
src/components/Login.tsx: Phase 3
```

Mark conflicts with `[warning]` for non-adjacent phases.

## Criteria Coverage Analysis Table

Display coverage matrix as markdown table:

```
## Criteria Coverage Analysis

| Criterion | Coverage | Phases |
|-----------|----------|--------|
| C1: Database schema defined | Good (2) | Phase 1, Phase 4 |
| C2: Migrations work | Good (2) | Phase 1, Phase 4 |
| C3: Auth endpoints respond | Good (3) | Phase 2, Phase 3, Phase 4 |
| C4: Sessions persist | Weak (1) | Phase 2 |
```

Coverage levels:
- **Good (2+):** Criterion addressed by multiple phases
- **Weak (1):** Only one phase addresses criterion
- **None (0):** Criterion not addressed (error)

## Summary Section

After detailed sections, include summary with:
- Total phase count
- Dependency validation status
- File conflict warnings
- File existence checks
- Verification step coverage
- Criteria coverage summary (e.g., "3/4 criteria have good coverage")
