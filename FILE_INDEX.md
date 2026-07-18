# Repository File Index

This file is generated and must not be edited manually.

The previous index was removed from authority because it listed deleted files and omitted current planning documents.

Before implementation handoff or release, run from the repository root:

```bash
python3 scripts/repository/generate_repository_metadata.py
```

That command regenerates:

- `FILE_INDEX.md`
- `MANIFEST_FILES.txt`
- `SHA256SUMS`

Until generation is run from a complete clean checkout, Git and the live GitHub tree are the only authoritative file inventory.
