# P-1140F Repair Head Review

Status: `pending-independent-semantic-review`
Updated: 2026-07-24

This record captures the repaired planning-contract head. It is not a security certification, runtime test, or P-1104 authorization.

## Repairs present on this head

- SR-001: OAuth transactions bind a preconfigured provider capability; callback input cannot select issuer, provider, client, redirect, or token endpoint. GitHub and X fixtures bind stored issuer/endpoints/redirects and reject redirect confusion.
- SR-002: ordinary desktop authentication is browser Authorization Code plus PKCE; device authorization requires a registered profile ID and fixtures reject ordinary desktop and CI paths.
- SR-003: `interactive-shell` is an authoritative local-only state machine with authenticated daemon-peer connection and explicit UI-exit/crash transitions that do not stop the daemon.
- SR-004: every platform source has canonical URI, immutable version/revision, retrieval instant, SHA-256 content digest, authority, and supported-field scope. Internal policy source binds an exact Git commit rather than `main`.

## Required closure evidence

1. GitHub Actions `Planning checks` passes on this exact commit, including PostgreSQL DDL validation.
2. An independent semantic reviewer confirms the four repairs satisfy the P-1140F criteria and finds no semantic P0/P1.
3. Only then may `P1140F_SEMANTIC_REVIEW_AND_STANDARDS_MAPPING_2026-07-24.md` transition to `complete-planning`; P-1104 remains a separate explicit user decision.
