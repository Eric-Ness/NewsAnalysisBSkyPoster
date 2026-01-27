---
type: prompt
name: tiki:release
description: Release management help - see /tiki:release-* commands
allowed-tools: ""
argument-hint: "[help]"
---

# Release

Release management commands for Tiki. These commands have been split into individual files for better maintainability.

## Available Commands

| Command | Description |
|---------|-------------|
| `/tiki:release-new <version>` | Create a new release version with interactive issue selection |
| `/tiki:release-status [version]` | Display release status and progress |
| `/tiki:release-add <issue> [--to <version>]` | Add one or more issues to a release with optional requirements mapping |
| `/tiki:release-remove <issue>` | Remove an issue from its release |
| `/tiki:release-ship <version>` | Ship a release (close issues, create tag, archive) |
| `/tiki:release-yolo <version>` | Automated release execution (plan, execute, ship all issues) |
| `/tiki:release-sync <version>` | Synchronize release state with GitHub milestone |

## Quick Start

### Create a new release

```text
/tiki:release-new v1.2
```

### View release status

```text
/tiki:release-status           # All releases
/tiki:release-status v1.2      # Specific release
```

### Add issues to a release

```text
/tiki:release-add 34                    # Add to active release
/tiki:release-add 34 35 36              # Add multiple issues
/tiki:release-add 34 --to v1.2          # Add to specific release
```

### Remove an issue from its release

```text
/tiki:release-remove 34
```

### Ship a release

```text
/tiki:release-ship v1.1
```

### Automated release execution (YOLO mode)

```text
/tiki:release-yolo v1.1                 # Full automation
/tiki:release-yolo v1.1 --dry-run       # Preview without changes
/tiki:release-yolo v1.1 --continue      # Resume after failure
```

### Sync with GitHub milestone

```text
/tiki:release-sync v1.2                 # Push local to GitHub
/tiki:release-sync v1.2 --pull          # Pull GitHub to local
/tiki:release-sync v1.2 --two-way       # Bi-directional sync
```

## Release State Files

Release state is stored in `.tiki/releases/`:

```text
.tiki/releases/
├── v1.0.json        # Shipped release (archived)
├── v1.1.json        # Active release
└── v1.2.json        # Draft release
```

## Common Workflows

### Standard Release Flow

1. `/tiki:release-new v1.2` - Create release
2. `/tiki:release-add 34 35` - Add issues
3. Work on issues with `/tiki:execute`
4. `/tiki:release-status v1.2` - Check progress
5. `/tiki:release-ship v1.2` - Ship when ready

### Automated Release (YOLO)

1. `/tiki:release-new v1.2` - Create release
2. `/tiki:release-add 34 35 36` - Add issues
3. `/tiki:release-yolo v1.2` - Execute all issues automatically
4. Release is shipped automatically on success

## Migration Note

The command syntax changed from subcommands to hyphenated commands:

| Before | After |
|--------|-------|
| `/tiki:release new v1.1` | `/tiki:release-new v1.1` |
| `/tiki:release status` | `/tiki:release-status` |
| `/tiki:release add 34` | `/tiki:release-add 34` |
| `/tiki:release remove 34` | `/tiki:release-remove 34` |
| `/tiki:release ship v1.1` | `/tiki:release-ship v1.1` |
| `/tiki:release yolo v1.1` | `/tiki:release-yolo v1.1` |
| `/tiki:release sync v1.2` | `/tiki:release-sync v1.2` |

This change improves command file maintainability while maintaining all functionality.
