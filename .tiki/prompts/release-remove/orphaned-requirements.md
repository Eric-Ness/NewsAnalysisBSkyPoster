# Orphaned Requirements Handling

Display this UI when removing an issue would leave requirements unaddressed by any other issue in the release.

## Warning Display

```text
### Orphaned Requirements Warning

Removing this issue will leave the following requirements unaddressed:

| ID | Requirement |
|----|-------------|
| {reqId} | {requirement description} |

These requirements will no longer be covered by any issue in release {version}.

How would you like to handle this?

1. **Keep requirements** - Remove issue but keep requirements in release tracking
2. **Clear requirements** - Remove issue and reset requirement counts
3. **Cancel** - Don't remove the issue

Enter choice:
```

## Option Handling

**Option 1: Keep requirements**

The requirements remain tracked but show as "not_covered" in status. Proceed to removal confirmation.

**Option 2: Clear requirements**

Update requirements totals after removal to reflect the removed coverage. Proceed to removal confirmation.

**Option 3: Cancel**

Exit immediately with message: "No changes made."

## No Orphans Case

If no orphaned requirements exist, skip this step entirely and proceed directly to removal confirmation.
