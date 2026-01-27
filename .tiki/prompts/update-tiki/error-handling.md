# Error Handling

Error handling guidance for update-tiki command.

## Network Errors

If unable to fetch remote version or clone repository:
- Report the error clearly
- Suggest checking internet connection
- Do not modify any local files

## Git Not Available

If `git clone` fails:
- Report that git is required
- Suggest installing git or using GitHub CLI

## Backup Failure

If unable to create backup:
- Stop the update process
- Report the error
- Do not proceed without backup

## Partial Update Failure

If copying files fails mid-process:
- Report which files were updated
- Point user to backup for recovery
- Suggest manual completion or retry
