# Category Management

Conditional prompt loaded when managing requirement categories.

## Category ID Conventions

| Code | Category | Description |
|------|----------|-------------|
| CORE | Core Functionality | Essential product features |
| PLAN | Planning | Planning and preparation capabilities |
| EXEC | Execution | Runtime behavior and execution flows |
| QUAL | Quality | Testing, reliability, code quality |
| DOC | Documentation | Documentation and help resources |
| PERF | Performance | Speed, scalability, efficiency |
| SEC | Security | Auth, authorization, data protection |

**Custom categories:** Use 2-4 letter codes (e.g., `UI`, `DATA`, `API`, `INTG`).

## Create Category Flow

```
1. Prompt: "Enter new category code (2-4 letters):"
2. Validate: uppercase, 2-4 chars, not existing
3. Prompt: "Enter category name:"
4. Create: { id: code.toLowerCase(), name: name, requirements: [] }
5. Confirm: "Created category: {CODE} - {Name}"
```

## Rename Category Flow

```
1. Show current categories with requirement counts
2. Prompt: "Which category to rename? Enter code:"
3. Prompt: "Enter new name (code stays same):"
4. Update category name in both files
5. Confirm: "Renamed {CODE}: {OldName} -> {NewName}"
```

## Merge Categories Flow

```
1. Show current categories with counts
2. Prompt: "Source category to merge FROM:"
3. Prompt: "Target category to merge INTO:"
4. For each requirement in source:
   - Generate new ID in target sequence
   - Move requirement, update ID
5. Delete empty source category
6. Confirm: "Merged {N} requirements from {SRC} into {TGT}"
```

## Move Requirement Flow

```
1. Prompt: "Which requirement to move? Enter ID:"
2. Show: "Current category: {CATEGORY} ({Name})"
3. Show target options with counts
4. Prompt: "Move to which category?"
5. Generate new ID in target sequence (e.g., QUAL-01 -> SEC-03)
6. Update requirement, preserve all other fields
7. Confirm: "Moved {OLD_ID} to {NEW_ID}"
```

## ID Generation

When adding to a category, find the next available number:
```
existing: [CORE-01, CORE-02, CORE-05]  # CORE-03, CORE-04 removed
next_id: CORE-06  # Always increment from highest
```

IDs are never reused after removal to maintain traceability.
