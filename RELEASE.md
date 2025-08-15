# Harbor v2 (Python) — Release Notes
 
 This branch migrates Harbor to a Python core executed inside a runner container.
 Use these steps during the v2 sprints. Legacy v1 guidance remains below.
 
 - Build runner image
   ```sh
   just -f bin/justfile build-runner
   ```
 - Tag and changelog (manual for now)
   - Versioning: annotate in commit and update CHANGE summary in this file
   - Tag on `v2` branch: `git tag -a v2.<x> -m "Harbor v2 <x>" && git push --tags`
 - Docs
   - README updated with v2 structure (etc/lib, etc/stacks, etc/runner, bin/justfile)
   - Export ConPort snapshot for records: see `conport_export/`
 
 ---
 
### Releasing Harbor

This is a helper documentation on release workflow.

### Seed values

Includes:
- seeding "current" version everywhere
- project scope for poetry for PyPi publishing

```bash
# Either
deno run -A ./.scripts/seed.ts
harbor dev seed
```

### Sync docs to wiki

```bash
# Either
deno run -A ./.scripts/docs.ts
harbor dev docs
```

### Publish to npm

```bash
# Test
npm publish --dry-run

# Publish
npm whoami
npm publish --access public
```

### Publish to PyPI

```bash
# System python
poetry env use system
# Build
poetry build -v
# Publish
poetry publish -v
```

### App/Docker builds

- Actions on GH, attached to a tag

### Script

1. Update version in `./.scripts/seed.ts`
2. Run the script `./.scripts/release.sh`
