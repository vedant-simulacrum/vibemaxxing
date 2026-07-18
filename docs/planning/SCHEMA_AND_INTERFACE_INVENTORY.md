# Schema and Interface Inventory

Status: normative planning evidence
Updated: 2026-07-19

## Normative artifacts required before implementation completion

| Artifact | Format | Authority | Compatibility rule |
|---|---|---|---|
| Adapter manifest | JSON Schema | adapter contract | additive fields only within major version |
| Normalized agent event | JSON Schema + Rust type | accounting/VibeProof contract | unknown fields rejected at trust boundary |
| VibeProof claim | CDDL + canonical CBOR | VibeProof contract | exact major-version negotiation |
| COSE signing profile | prose + vectors | VibeProof contract | protected algorithm and key-id required |
| Local IPC | Protobuf | native runtime contract | negotiated major/minor; bounded messages |
| Public HTTP API | OpenAPI 3.1 | server contract | versioned `/v1`; additive compatible changes |
| Internal service messages | Protobuf/Buf | server contract | Buf breaking-change checks |
| PostgreSQL model | SQL migrations | server contract | expand/migrate/contract |
| Reason codes | JSON registry | integrity contract | stable identifiers never reused |
| Evidence qualification | JSON rules | integrity contract | policy version recorded on claim decision |
| Notification events | Protobuf/JSON schema | social contract | idempotent event IDs |
| Moderation/appeal events | Protobuf/JSON schema | integrity contract | append-only audit chain |
| Observability allowlist | YAML/JSON schema | operations contract | deny by default |

## Required VibeProof fields

Protocol version, claim ID, account pseudonym, device key ID, adapter ID/version, source family/version, session ID, sequence, previous-claim hash, challenge ID, observed-at bucket, token categories, accounting-policy version, evidence state, platform-capability code, local claim commitment, issued-at, expiry, and protected signature metadata.

Forbidden fields include prompts, responses, code, diffs, paths, repository/project names, tool payloads, credentials, free text, embeddings, summaries, classifications, and personal insights.

## Public API groups

`/auth`, `/sessions`, `/identities`, `/devices`, `/claims`, `/leaderboards`, `/profiles`, `/friends`, `/blocks`, `/rivals`, `/boards`, `/organizations`, `/communities`, `/countries`, `/presence`, `/notifications`, `/moderation`, `/appeals`, `/exports`, and `/deletions`.

Every mutating endpoint requires authentication, authorization, request ID, idempotency behavior, rate limit, privacy class, stable error code, audit behavior, and deletion/retention ownership.

## PostgreSQL entity groups

Accounts, linked identities, sessions, stronger factors, devices, device keys, adapter installations, challenges, accepted claims, rejected-claim summaries, sequence heads, claim corrections, outbox, worker checkpoints, minute scores, period scores, pricing datasets, profiles, friendships, blocks, rivals, boards, memberships, presence leases, notifications, moderation cases, actions, appeals, exports, deletion jobs, and privacy-safe audit events.

## Validation rules

All schemas must parse in CI once implementation mode opens. Examples must validate against their schema. Generated clients and types must be reproducible. Breaking changes require a major protocol/API version and migration plan. No prose-only interface may be treated as sufficient once its implementation begins.