# Interactive Refinement Mode

**Load Condition:** User did not select `--auto-accept` flag OR user explicitly requests refinement

This prompt handles Step 6 of define-requirements: iterative refinement of proposed requirements.

---

## 6a: Present Refinement Options

Use AskUserQuestion to present:

```
## Requirement Refinement

{count} requirements proposed. What would you like to do?

1. **Accept** - Save these requirements as-is
2. **Edit** - Modify a requirement (e.g., "Edit CORE-04")
3. **Add** - Create a new requirement
4. **Remove** - Delete a requirement (e.g., "Remove QUAL-02")
5. **Reorganize** - Move between categories or rename categories
6. **Review flagged** - Examine flagged requirements

Enter your choice:
```

---

## 6b: Edit Operation

When user selects "Edit" or "Edit {ID}":

1. Display current values: ID, Text, Category, Status, Verification, Source
2. Offer field selection: Text, Category, Verification, Status, All fields, Cancel
3. Collect new value and confirm update
4. Return to main menu

---

## 6c: Add Operation

Guide user through 4 steps:

1. **Category**: Select existing or create new category
2. **Text**: Use "System shall..." format
3. **Verification**: Choose type (automated_test, manual_test, code_review, state_check, documentation) with description
4. **Status**: pending (default), implemented, or partial

Assign next available ID in category sequence (e.g., CORE-05).

---

## 6d: Remove Operation

When user selects "Remove" or "Remove {ID}":

1. Show requirement details and source
2. Confirm: Remove, Keep, or Move instead
3. If removed, preserve other IDs (no renumbering)
4. Return to main menu

---

## 6e: Reorganize Operation

Options:
- Move requirement to different category (renumber ID)
- Create new category
- Rename existing category
- Merge two categories
- View category breakdown

When moving: assign new ID in target category sequence.

---

## 6f: Loop Until Accept

Track changes during session:
```
changesLog = []
After each operation: { action, requirementId, timestamp, details }
```

When user selects "Accept":

1. Display changes summary (edits, adds, removes, moves)
2. Show final counts by category and status
3. Ask: "Proceed to save? [Yes / Make more changes]"
4. If confirmed, proceed to Step 7 (output generation)

---

## Output Confirmation

After save:
```
Writing requirements...
- Created: .tiki/REQUIREMENTS.md
- Created: .tiki/requirements.json

Requirements saved successfully.

### Next Steps
1. Review .tiki/REQUIREMENTS.md
2. Use in planning - /tiki:plan-issue references requirements
3. Track implementation via implementedBy links
4. Update later with /tiki:define-requirements
```
