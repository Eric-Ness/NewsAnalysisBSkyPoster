# Audit Fix Suggestions

Guidance for resolving audit issues found during plan validation.

## Phase Size Issues

**Too many tasks (>10):**
- Split into logical sub-phases by functionality
- Group related tasks together
- Each sub-phase should have 4-7 focused tasks

**Too many files (>15):**
- Separate by layer (models, routes, components)
- Create dedicated phases for cross-cutting concerns
- Consider if some files can be handled in later phases

## Dependency Issues

**Circular dependency detected:**
1. Identify the cycle (e.g., Phase 2 -> Phase 4 -> Phase 2)
2. Determine which dependency can be removed or deferred
3. Consider extracting shared work into an earlier phase
4. Re-order phases to break the cycle

**Forward dependency (depends on later phase):**
- Move the depended-upon work earlier
- Swap phase order if possible
- Extract common setup into Phase 1

## File Conflict Resolution

**Non-adjacent phases modify same file:**
- Consolidate all changes to that file into one phase
- If changes are unrelated, document the conflict explicitly
- Consider if changes can be made sequential

**Many phases touch same file:**
- Create a dedicated phase for that file
- Refactor to reduce coupling
- Split the file if it has multiple responsibilities

## Criteria Coverage Improvements

**Criterion not covered (0 tasks):**
- Add a new phase specifically for this criterion
- Expand an existing phase to include tasks addressing it
- Verify the criterion is actually required

**Weak coverage (1 task):**
- Add verification tasks to strengthen coverage
- Include the criterion in testing phase
- Add implementation tasks in additional phases

## General Recommendations

After fixing issues:
1. Run `/tiki:audit-plan` again to verify fixes
2. Use `/tiki:discuss-phases` for interactive adjustments
3. Consider `/tiki:plan-issue` for major restructuring
