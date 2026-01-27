# Example Outputs

Reference examples for update-tiki command output formatting.

## Already Up to Date

```
## Tiki Update Check

Local version:  1.2.0
Remote version: 1.2.0

Tiki is already up to date!
```

## Update Available

```
## Tiki Update Check

Local version:  1.0.0
Remote version: 1.2.0

### What's New

**Version 1.2.0** (2026-01-20)
- Added /tiki:heal command for auto-fixing failed phases
- Improved phase dependency validation
- Fixed issue with pause/resume state

**Version 1.1.0** (2026-01-17)
- Added TDD support with test-creator
- New assess-code command for codebase health checks

### Updating...

Backing up to .tiki/backups/commands-20260121-143022/

Cloning latest Tiki...

Copying files:
  add-issue.md (unchanged)
  assess-code.md (updated)
  execute.md (updated)
  heal.md (new)
  plan-issue.md (updated)
  ...

Cleaning up...

## Update Complete!

Tiki updated from 1.0.0 to 1.2.0

3 files updated, 1 new file, 19 unchanged

Backup saved to: .tiki/backups/commands-20260121-143022/
```

## Dry Run

```
## Tiki Update Check (Dry Run)

Local version:  1.0.0
Remote version: 1.2.0

Would update the following files:
- assess-code.md
- execute.md
- heal.md (new)
- plan-issue.md
- test-creator.md
- update-tiki.md
- version.json

Run without --dry-run to apply updates.
```
