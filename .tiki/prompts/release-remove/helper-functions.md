# Release Remove Helper Functions

JavaScript pseudocode for release removal operations.

## findReleaseForIssue(issueNumber)

Finds which release contains a specific issue.

```javascript
function findReleaseForIssue(issueNumber) {
  // Glob for all active release files
  const releaseFiles = glob('.tiki/releases/*.json');

  for (const file of releaseFiles) {
    const release = readJSON(file);
    const issue = release.issues.find(i => i.number === issueNumber);
    if (issue) {
      return { release, version: release.version, filePath: file };
    }
  }

  return null; // Issue not in any release
}
```

## saveRelease(version, data)

Saves a release file to the appropriate location.

```javascript
function saveRelease(version, data) {
  const normalized = version.startsWith('v') ? version : `v${version}`;

  if (data.status === 'shipped') {
    // Save to archive
    const path = `.tiki/releases/archive/${normalized}.json`;
    writeJSON(path, data);
  } else {
    // Save to active releases
    const path = `.tiki/releases/${normalized}.json`;
    writeJSON(path, data);
  }
}
```

## findOrphanedRequirements(release, issueNumber)

Checks if removing an issue would leave requirements orphaned.

```javascript
function findOrphanedRequirements(release, issueNumber) {
  const issueToRemove = release.issues.find(i => i.number === issueNumber);
  if (!issueToRemove || !issueToRemove.requirements?.length) {
    return [];
  }

  const orphaned = [];

  for (const reqId of issueToRemove.requirements) {
    // Check if any other issue in the release addresses this requirement
    const otherIssueWithReq = release.issues.find(i =>
      i.number !== issueNumber &&
      i.requirements?.includes(reqId)
    );

    if (!otherIssueWithReq) {
      orphaned.push(reqId);
    }
  }

  return orphaned;
}
```
