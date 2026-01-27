# Rollback and Error Handling

Instructions for handling errors during release ship.

## Common Errors

### Release Not Found

```
Release "{version}" not found.

Available releases:
{List active and archived releases}

Create new: /tiki:release-new {version}
```

### GitHub API Errors

```
Unable to verify issue states from GitHub.
Error: {error}

Options:
1. Retry - Try verification again
2. Skip verification - Ship without GitHub verification
3. Cancel - Exit and fix the issue
```

### Git Tag Errors

```
Failed to create git tag "{version}": {error}

Fixes:
- Tag exists: git tag -d {version} && git tag -a {version} -m "Release {version}"
- Dirty directory: Commit or stash changes
- Not git repo: Initialize git or skip tagging

Release archived. Create tag manually if needed.
```

### Archive Errors

```
Unable to write archive file.
Error: {error}

Fix: mkdir -p .tiki/releases/archive
Retry: /tiki:release-ship {version}
```

### Corrupted Release File

```
Unable to parse: .tiki/releases/{version}.json
Error: {parse error}

Options:
1. View raw: cat .tiki/releases/{version}.json
2. Restore backup
3. Recreate: /tiki:release-new {version}
```

## Edge Cases

- **Empty release**: Must have at least one issue
- **All issues removed**: Release becomes empty, cannot ship
- **Requirements file missing**: Continue without or define first
