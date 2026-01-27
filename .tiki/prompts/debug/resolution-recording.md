# Resolution Recording

Conditionally loaded when marking session as resolved or abandoned.

## Record Root Cause

Prompt user for:
1. **What** is broken? (component/function/behavior)
2. **Why** did it break? (underlying cause)
3. **Trigger** - what conditions trigger it?

Update session document's Root Cause section:

```markdown
## Root Cause

**Component:** {what}
**Cause:** {why}
**Trigger:** {trigger}
```

## Record Solution

Present options:
1. **Describe solution** - Document planned fix
2. **Implement fix** - Apply fix with assistance
3. **Already fixed** - Document what was done

For option 1-2, capture:
- Approach taken
- Key changes made
- Files modified

Update Solution Applied section:

```markdown
## Solution Applied

**Approach:** {approach}
**Changes:**
- {change_1}
- {change_2}

**Files Modified:** {file_list}

**Verified:** {yes/no with method}
```

## Capture Lessons Learned

Prompt for:
- **Prevention:** How to prevent similar issues?
- **Detection:** How to catch this earlier?
- **Process:** Any workflow improvements?

Update Lessons Learned section:

```markdown
## Lessons Learned

- **Prevention:** {prevention_strategy}
- **Detection:** {detection_improvement}
- **Process:** {process_change}
```

## Mark Session Resolved

1. Update Session Info table:
   - Status: `Resolved`
   - Resolved: `{current_date}`
   - Last Updated: `{current_date}`

2. Update index via index-management.md:
   - Set `status: "resolved"`
   - Add `resolvedAt` timestamp
   - Populate `rootCause`, `solution`, `keywords`

3. Display: `Session marked as resolved. Run '/tiki:debug list' to view all sessions.`

## Pause Session

When user chooses to pause:

1. Update Session Info:
   - Status: `In Progress (Paused)`
   - Last Updated: `{current_date}`

2. Record current state in session file:
   ```markdown
   ## Paused State

   **Current Hypothesis:** {active_hypothesis}
   **Next Steps:** {planned_next_steps}
   **Notes:** {user_notes}
   ```

3. Update index: set `status: "paused"`

4. Display: `Session paused. Resume with '/tiki:debug --resume'`

## Abandon Session

When user chooses to abandon:

1. Ask for reason (required):
   - Dead end / not reproducible
   - Issue no longer relevant
   - Resolved elsewhere
   - Other: {reason}

2. Update Session Info:
   - Status: `Abandoned`
   - Abandoned: `{current_date}`
   - Reason: `{reason}`

3. Update index via index-management.md:
   - Set `status: "abandoned"`
   - Add `abandonedAt` timestamp
   - Record `abandonReason`

4. Preserve session file for future reference

5. Display: `Session abandoned: {reason}. Session preserved at {filepath}.`
