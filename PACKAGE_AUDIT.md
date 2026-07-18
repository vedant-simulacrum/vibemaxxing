# Authoritative Package Audit

## Purpose

This directory is the complete manually uploadable VibeMaxxing repository assembled from the latest authoritative project tree and all current top-level control documents.

## Included

- Product and design context
- VibeProof protocol and privacy contract
- Architecture and accepted ADRs
- Research audits through Wave 5
- Agent integration research
- Token accounting specification
- Security, abuse, authentication, IPC, and platform-isolation guidance
- Implementation roadmap and current status
- Research and evidence backlog
- CI, security, release, dependency, and repository-policy workflows
- Eval registry and runners
- Conformance and adversarial fixtures
- PostgreSQL benchmark seeds
- Go API scaffold and Rust/TypeScript project structure
- Production readiness, SLO, incident response, observability, release verification, data lifecycle, and recovery requirements
- ChatGPT Work and coding-agent prompts
- File index, manifest, and SHA-256 checksums

## Deliberately excluded

- `.git` history from temporary local preparations
- `bootstrap-import/`
- Base64 archive chunks
- One-use bootstrap GitHub Actions workflows
- Python bytecode and `__pycache__`
- Obsolete VM/control-plane architecture
- Older duplicate ZIP packages inside the repository

## Verification

From the repository root:

```bash
sha256sum -c SHA256SUMS
```

The command should report every tracked package file as `OK`.

`MANIFEST_FILES.txt` lists all files covered by the checksum set. `FILE_INDEX.md` provides a human-readable grouped index.
