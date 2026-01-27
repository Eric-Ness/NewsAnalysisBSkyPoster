# Manual Verification Workflow

Interactive verification for items that cannot be automated.

## Prompt Format

Display verification context before each prompt:

```
## Verification: {phase_title}

**Item:** {verification_text}

Options:
1. Pass - Verified working correctly
2. Fail - Issue found (will prompt for details)
3. Skip - Cannot verify now
4. Need Info - Requires clarification
```

## Using AskUserQuestion

For each manual item, call AskUserQuestion with options:
- "Pass" (description: "Verified working correctly")
- "Fail" (description: "Issue found - will prompt for details")
- "Skip" (description: "Cannot verify now")
- "Need Info" (description: "Requires clarification before verifying")

## Handling User Responses

**Pass:**
- Mark item status as `pass`
- Set `verifiedAt` to current ISO timestamp
- Proceed to next item

**Fail:**
Prompt for details: "Please describe the issue found:"
- Mark item status as `fail`
- Set `verifiedAt` to current ISO timestamp
- Store description in `notes`

**Skip:**
Optional prompt: "(Optional) Why are you skipping this item?"
- Mark item status as `skip`
- Set `verifiedAt` to current ISO timestamp
- Store reason in `notes` if provided

**Need Info:**
Prompt: "What clarification do you need for this item?"
- Mark item status as `pending`
- Store question in `notes`
- Item appears in summary as needing clarification

## Example Interaction

```
## Verification: Add authentication endpoints

**Item:** POST /auth/login returns JWT token

[User selects: Fail]

Please describe the issue found:
> "Returns 500 error when password contains special characters"

[Stored in notes, proceeding to next item]
```
