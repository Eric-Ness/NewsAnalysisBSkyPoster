# Phase Adjustment Operations

Reference guide for processing user-requested phase adjustments. Each operation includes the workflow, example dialog, and edge case handling.

---

## Split a Phase

**Trigger:** User requests splitting a phase (e.g., "split phase 2 into login and token refresh")

**Process:**
1. Read the phase content
2. Create two new phases with split content
3. Renumber subsequent phases
4. Update dependencies

**Example Dialog:**
```
Splitting Phase 2...

**New Phase 2: Add login endpoint**
- Files: src/routes/auth.ts
- Tasks: Implement /api/login, validate credentials

**New Phase 3: Add token refresh**
- Files: src/routes/auth.ts, src/services/token.ts
- Dependencies: Phase 2
- Tasks: Implement /api/refresh, validate refresh tokens

Phase 4 (was 3): Add protected routes
- Dependencies updated: Phase 1, 2, 3

Save changes? [Yes/No]
```

---

## Merge Phases

**Trigger:** User requests merging phases (e.g., "merge phases 2 and 3")

**Process:**
1. Combine content from both phases
2. Merge file lists
3. Take earliest dependencies
4. Renumber subsequent phases

**Example Dialog:**
```
Merging Phases 2 and 3...

**New Phase 2: Add login and protected routes**
- Files: src/routes/auth.ts, src/services/auth.ts, src/routes/user.ts
- Dependencies: Phase 1
- Tasks: Combined from both phases

Warning: Merged phase has 8 tasks and 4 files - verify it fits in one context window.

Save changes? [Yes/No]
```

**Warning:** Always warn if merged phase exceeds recommended limits (>10 tasks or >15 files).

---

## Reorder Phases

**Trigger:** User requests moving a phase (e.g., "move phase 3 to phase 1")

**Process:**
1. Validate the move doesn't break dependencies
2. Renumber phases
3. Update all dependency references

**Example Dialog (Success):**
```
Reordering phases...

Before:
1. Setup auth middleware
2. Add login endpoint
3. Add protected routes

After:
1. Add protected routes (was 3)
2. Setup auth middleware (was 1)
3. Add login endpoint (was 2)
```

**Example Dialog (Error):**
```
Error: Cannot move Phase 3 to position 1 - it depends on Phase 1 and 2.

Suggested alternatives:
- Move Phase 2 to position 3 instead
- Remove dependencies from Phase 3 first
```

**Key Rule:** Dependencies must flow forward - Phase N can only depend on phases 1 to N-1.

---

## Modify a Phase

**Trigger:** User requests adding/changing content (e.g., "add rate limiting to phase 2")

**Process:**
1. Update the phase content
2. Add new files if needed
3. Extend verification steps

**Example Dialog:**
```
Updating Phase 2...

Added to Phase 2:
- Task: "Implement rate limiting for login endpoint"
- File: src/middleware/rateLimit.ts
- Verification: "Rate limiting blocks after 5 failed attempts"

Save changes? [Yes/No]
```

---

## Add a Phase

**Trigger:** User requests a new phase (e.g., "add a phase for password reset")

**Process:**
1. Determine appropriate position
2. Create new phase with user-provided details
3. Renumber subsequent phases

**Example Dialog:**
```
Adding new phase...

Where should this phase go?
- After Phase 2 (before protected routes)
- After Phase 3 (at the end)

User: "after phase 3"

**New Phase 4: Add password reset**
- Priority: medium
- Files: [to be determined]
- Dependencies: Phase 1, 2

Please provide more details:
- What files will this phase modify?
- What are the main tasks?
```

**Prompt for details:** Always ask for files and tasks if not provided.

---

## Remove a Phase

**Trigger:** User requests removal (e.g., "remove phase 3")

**Process:**
1. Check for dependent phases
2. Remove the phase
3. Renumber subsequent phases
4. Update dependencies

**Example Dialog (With Dependencies):**
```
Removing Phase 3...

Warning: Phase 4 depends on Phase 3.

Options:
1. Remove Phase 3 and update Phase 4 dependencies to [1, 2]
2. Remove Phase 3 and Phase 4
3. Cancel

Which option? [1/2/3]
```

**Key Rule:** Always check for and handle dependent phases before removal.

---

## Confirmation Pattern

All operations should follow this confirmation flow:

1. Show preview of changes
2. Display any warnings (size limits, dependency changes)
3. Ask "Save changes? [Yes/No]"
4. On Yes: Write updated plan, show validation summary
5. On No: Discard changes, return to adjustment menu
